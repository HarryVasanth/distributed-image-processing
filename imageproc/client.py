"""Command line client for the distributed image processing cluster."""

from __future__ import annotations

import argparse
import contextlib
import logging
import sys
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any
from urllib.parse import urlparse

import cv2
import numpy as np
import requests

from . import __version__, tasks
from .codec import decode_image, encode_image
from .config import settings
from .imaging import list_images, load_image, result_path, save_image, split_image
from .reporting import CsvReporter

LOGGER = logging.getLogger(__name__)


class ProcessingError(RuntimeError):
    """Raised when a worker task fails or returns an unusable result."""


def _as_float(value: Any) -> float:
    return float(str(value))


def _as_int(value: Any) -> int:
    return int(str(value))


def _as_points(value: Any) -> list[float]:
    if isinstance(value, (list, tuple)):
        numbers = list(value)
    else:
        numbers = [part.strip() for part in str(value).split(",") if part.strip()]
    if len(numbers) != 8:
        raise ValueError("expected eight comma-separated numbers (x1,y1,...,x4,y4)")
    return [float(number) for number in numbers]


@dataclass(frozen=True)
class Parameter:
    name: str
    prompt: str
    default: Any = None
    cast: Callable[[Any], Any] = _as_float


@dataclass(frozen=True)
class Algorithm:
    name: str
    task: Any
    help: str
    parameters: tuple[Parameter, ...] = ()
    supports_split: bool = True


ALGORITHMS: dict[str, Algorithm] = {
    "edge_detection": Algorithm(
        "edge_detection",
        tasks.edge_detection,
        "Canny edges with median-derived thresholds.",
        (Parameter("sigma", "Threshold spread (0-1)", 0.33),),
    ),
    "thresholding": Algorithm(
        "thresholding",
        tasks.thresholding,
        "Binary threshold; above the cut-off becomes white.",
        (
            Parameter("threshold", "Threshold (0-255)", 127, _as_int),
            Parameter("max_value", "Value above threshold (0-255)", 255, _as_int),
        ),
    ),
    "scaling": Algorithm(
        "scaling",
        tasks.scaling,
        "Resize by independent x/y factors.",
        (
            Parameter("scale_x", "Horizontal scale", 1.0),
            Parameter("scale_y", "Vertical scale (blank = same as x)", None),
        ),
    ),
    "translation": Algorithm(
        "translation",
        tasks.translation,
        "Shift the image by a pixel offset.",
        (
            Parameter("tx", "Horizontal offset in pixels", 0.0),
            Parameter("ty", "Vertical offset in pixels", 0.0),
        ),
        supports_split=False,
    ),
    "rotation": Algorithm(
        "rotation",
        tasks.rotation,
        "Rotate around the centre and optionally scale.",
        (
            Parameter("angle", "Angle in degrees", 0.0),
            Parameter("scale", "Isotropic scale", 1.0),
        ),
        supports_split=False,
    ),
    "perspective": Algorithm(
        "perspective",
        tasks.perspective,
        "Four-point perspective transform (corners inset by default).",
        (
            Parameter("src", "Source points x1,y1,...,x4,y4 (blank = corners)", None, _as_points),
            Parameter("dst", "Target points x1,y1,...,x4,y4 (blank = inset)", None, _as_points),
        ),
        supports_split=False,
    ),
    "smooth_average": Algorithm(
        "smooth_average",
        tasks.smooth_average,
        "Box-filter blur.",
        (
            Parameter("kernel_x", "Kernel width (odd)", 5, _as_int),
            Parameter("kernel_y", "Kernel height (odd)", 5, _as_int),
        ),
    ),
    "smooth_blur": Algorithm(
        "smooth_blur",
        tasks.smooth_blur,
        "Gaussian blur.",
        (
            Parameter("kernel_x", "Kernel width (odd)", 5, _as_int),
            Parameter("kernel_y", "Kernel height (odd)", 5, _as_int),
        ),
    ),
    "laplacian": Algorithm(
        "laplacian",
        tasks.laplacian,
        "Laplacian derivative, normalised for display.",
    ),
}


def parse_params(algorithm: Algorithm, assignments: Iterable[str]) -> dict[str, Any]:
    """Validate ``name=value`` overrides for an algorithm."""
    known = {parameter.name: parameter for parameter in algorithm.parameters}
    params = {
        parameter.name: parameter.default
        for parameter in algorithm.parameters
        if parameter.default is not None
    }
    for assignment in assignments:
        name, separator, raw = assignment.partition("=")
        name = name.strip()
        if not separator or not name:
            raise ValueError(f"expected NAME=VALUE, got {assignment!r}")
        if name not in known:
            expected = ", ".join(sorted(known)) or "none"
            raise ValueError(f"unknown parameter {name!r}; expected one of: {expected}")
        try:
            params[name] = known[name].cast(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid value for {name}: {exc}") from exc
    return params


class ProcessingClient:
    """Submit chunks to Celery and collect decoded results."""

    def __init__(
        self,
        *,
        flower_url: str | None = None,
        poll_interval: float | None = None,
        timeout: float | None = None,
        reporter: CsvReporter | None = None,
    ) -> None:
        self.flower_url = settings.flower_url if flower_url is None else (flower_url or None)
        if self.flower_url:
            parsed = urlparse(self.flower_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("Flower URL must be an http(s) URL")
            self.flower_url = self.flower_url.rstrip("/")
        self.poll_interval = settings.poll_interval if poll_interval is None else poll_interval
        self.timeout = settings.task_timeout if timeout is None else timeout
        if self.poll_interval <= 0 or self.timeout <= 0:
            raise ValueError("poll interval and timeout must be greater than zero")
        self.reporter = reporter
        self._session = requests.Session()

    def __enter__(self) -> ProcessingClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self._session.close()

    def process(
        self,
        image: np.ndarray,
        algorithm: Algorithm,
        params: dict[str, Any] | None = None,
        *,
        split: bool | None = None,
    ) -> np.ndarray:
        """Run one image through an algorithm and return the merged result."""
        use_split = algorithm.supports_split if split is None else split
        if use_split and not algorithm.supports_split:
            raise ValueError(f"{algorithm.name} does not support chunked processing")
        chunks = split_image(image, settings.chunks) if use_split else [image]
        payloads = [encode_image(chunk) for chunk in chunks]
        async_results = [algorithm.task.delay(payload, **(params or {})) for payload in payloads]
        outputs = self._collect(async_results)
        if not use_split:
            return outputs[0]
        try:
            return np.vstack(outputs)
        except ValueError as exc:
            raise ProcessingError("worker results could not be merged") from exc

    def _collect(self, async_results: Sequence[Any]) -> list[np.ndarray]:
        pending = list(enumerate(async_results))
        outputs: list[np.ndarray | None] = [None] * len(async_results)
        deadline = time.monotonic() + self.timeout

        while pending:
            for index, result in list(pending):
                if not result.ready():
                    continue
                try:
                    outputs[index] = decode_image(result.get(propagate=True))
                except Exception as exc:
                    raise ProcessingError(f"task {result.id} failed") from exc
                self._record(result)
                pending.remove((index, result))
            if not pending:
                break
            if time.monotonic() >= deadline:
                for _, result in pending:
                    with contextlib.suppress(Exception):
                        result.revoke()
                ids = ", ".join(result.id for _, result in pending)
                raise TimeoutError(f"timed out after {self.timeout:.0f}s waiting for: {ids}")
            time.sleep(self.poll_interval)

        if any(output is None for output in outputs):
            raise ProcessingError("one or more tasks returned no result")
        return [output for output in outputs if output is not None]

    def _record(self, result: Any) -> None:
        if not self.flower_url or self.reporter is None:
            return
        try:
            response = self._session.get(f"{self.flower_url}/api/task/info/{result.id}", timeout=5)
            response.raise_for_status()
            info = response.json()
            if isinstance(info, dict):
                self.reporter.write(info)
        except (requests.RequestException, ValueError) as exc:
            # Metrics are optional; never fail a job because Flower is down.
            LOGGER.debug("could not fetch Flower metrics for %s: %s", result.id, exc)


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected an integer, got {value!r}") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imageproc",
        description="Run OpenCV algorithms locally or across Celery workers.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--image", help="process a single image")
    parser.add_argument("--folder", help="process every supported image in a folder")
    parser.add_argument("--algorithm", choices=sorted(ALGORITHMS), help="algorithm to run")
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="algorithm parameter (repeatable)",
    )
    parser.add_argument("--runs", type=_positive_int, default=1, help="timed repetitions")
    parser.add_argument("--results-dir", default="results", help="output directory")
    parser.add_argument("--report-dir", help="write Flower CSV metrics to this directory")
    parser.add_argument("--flower-url", help="override IMAGEPROC_FLOWER_URL")
    parser.add_argument("--no-split", action="store_true", help="send the whole image in one task")
    parser.add_argument("--no-save", action="store_true", help="do not write result images")
    parser.add_argument("--load-color", action="store_true", help="load images in colour")
    parser.add_argument("--list-algorithms", action="store_true", help="show available algorithms")
    return parser


def run_batch(
    sources: Sequence[Path],
    algorithm: Algorithm,
    params: dict[str, Any],
    *,
    split: bool,
    runs: int,
    load_flag: int,
    results_dir: Path,
    save: bool,
    client: ProcessingClient,
) -> tuple[int, int]:
    """Run ``runs`` passes over ``sources``; return ``(failures, successes)``."""
    timings: list[float] = []
    failures = 0
    successes = 0
    for run in range(1, runs + 1):
        started = time.perf_counter()
        for source in sources:
            try:
                image = load_image(source, load_flag)
                output = client.process(image, algorithm, params, split=split)
                if save:
                    save_image(output, result_path(source, results_dir, algorithm.name))
                successes += 1
            except Exception as exc:
                failures += 1
                print(f"{source}: {exc}", file=sys.stderr)
        timings.append(time.perf_counter() - started)
        print(f"run {run}/{runs}: {timings[-1]:.3f}s")
    if runs > 1:
        print(
            f"mean wall time: {mean(timings):.3f}s "
            f"(min {min(timings):.3f}s, max {max(timings):.3f}s)"
        )
    return failures, successes


def _run_sources(
    sources: Sequence[Path],
    algorithm: Algorithm,
    params: dict[str, Any],
    *,
    split: bool,
    runs: int,
    load_flag: int,
    results_dir: Path,
    save: bool,
    report_dir: Path | None,
    flower_url: str | None,
) -> tuple[int, int]:
    reporter_context = (
        CsvReporter(report_dir, f"{algorithm.name}_{datetime.now():%Y%m%d_%H%M%S}")
        if report_dir
        else contextlib.nullcontext()
    )
    with (
        reporter_context as reporter,
        ProcessingClient(flower_url=flower_url, reporter=reporter) as client,
    ):
        return run_batch(
            sources,
            algorithm,
            params,
            split=split,
            runs=runs,
            load_flag=load_flag,
            results_dir=results_dir,
            save=save,
            client=client,
        )


def _print_algorithms() -> None:
    print(f"{'name':<18} {'split':<6} description")
    for algorithm in ALGORITHMS.values():
        split = "yes" if algorithm.supports_split else "no"
        print(f"{algorithm.name:<18} {split:<6} {algorithm.help}")
        for parameter in algorithm.parameters:
            print(f"  --param {parameter.name}=VALUE  ({parameter.prompt})")


def _choose_algorithm() -> Algorithm | None:
    names = list(ALGORITHMS)
    for index, name in enumerate(names, start=1):
        print(f"{index}. {name} - {ALGORITHMS[name].help}")
    choice = input("Algorithm (number, name, or blank to cancel): ").strip().lower()
    if not choice:
        return None
    if choice.isdigit() and 1 <= int(choice) <= len(names):
        return ALGORITHMS[names[int(choice) - 1]]
    return ALGORITHMS.get(choice)


def _prompt_params(algorithm: Algorithm) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for parameter in algorithm.parameters:
        default = "" if parameter.default is None else str(parameter.default)
        while True:
            raw = input(f"{parameter.prompt} [{default or 'default'}]: ").strip()
            if not raw:
                if parameter.default is not None:
                    params[parameter.name] = parameter.default
                break
            try:
                params[parameter.name] = parameter.cast(raw)
                break
            except (TypeError, ValueError) as exc:
                print(f"  {exc}")
    return params


def interactive_main() -> int:
    print(f"Distributed Image Processing {__version__}")
    while True:
        print("\n1. Process a single image")
        print("2. Process an image folder")
        print("3. List algorithms")
        print("9. Quit")
        choice = input("What would you like to do? ").strip()
        if choice == "9":
            print("Goodbye")
            return 0
        if choice == "3":
            _print_algorithms()
            continue
        if choice not in {"1", "2"}:
            print("Not a valid choice, please try again.")
            continue

        algorithm = _choose_algorithm()
        if algorithm is None:
            continue
        params = _prompt_params(algorithm)
        try:
            if choice == "1":
                path = input("Image path: ").strip()
                sources = [Path(path)] if path else []
            else:
                sources = list_images(input("Image folder: ").strip())
            if not sources:
                print("No images found.")
                continue
            runs = _positive_int(input("Number of runs [1]: ").strip() or "1")
            split = algorithm.supports_split
            if split:
                answer = input(f"Split across {settings.chunks} workers? [Y/n]: ")
                split = answer.strip().lower() not in {"n", "no"}
            load_flag = (
                cv2.IMREAD_COLOR
                if input("Load in colour? [y/N]: ").strip().lower()
                in {
                    "y",
                    "yes",
                }
                else cv2.IMREAD_GRAYSCALE
            )
            failures, successes = _run_sources(
                sources,
                algorithm,
                params,
                split=split,
                runs=runs,
                load_flag=load_flag,
                results_dir=Path("results"),
                save=True,
                report_dir=None,
                flower_url=None,
            )
            print(f"finished: {successes} succeeded, {failures} failed")
        except (KeyboardInterrupt, EOFError):
            print("\ncancelled")
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list_algorithms:
        _print_algorithms()
        return 0
    if not args.image and not args.folder:
        try:
            return interactive_main()
        except (KeyboardInterrupt, EOFError):
            print()
            return 130

    if args.image and args.folder:
        parser.error("use either --image or --folder, not both")
    if not args.algorithm:
        parser.error("--algorithm is required when using --image or --folder")

    algorithm = ALGORITHMS[args.algorithm]
    try:
        params = parse_params(algorithm, args.param)
        sources = [Path(args.image)] if args.image else list_images(args.folder)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not sources:
        print(f"error: no supported images found in {args.folder}", file=sys.stderr)
        return 1

    failures, successes = _run_sources(
        sources,
        algorithm,
        params,
        split=algorithm.supports_split and not args.no_split,
        runs=args.runs,
        load_flag=cv2.IMREAD_COLOR if args.load_color else cv2.IMREAD_GRAYSCALE,
        results_dir=Path(args.results_dir),
        save=not args.no_save,
        report_dir=Path(args.report_dir) if args.report_dir else None,
        flower_url=args.flower_url,
    )
    if successes == 0:
        return 1
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
