"""CSV reporting for Flower task metrics."""

from __future__ import annotations

import csv
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

FIELDS = [
    "TaskUID",
    "Task",
    "Task Received",
    "Task Started",
    "Task Succeed",
    "Runtime",
    "Time Between Reception And Start Processing (s)",
    "Processing Time (s)",
    "Total Time(s)",
    "WorkerName",
]


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _suffix(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None:
        return None
    return current - previous


def _blank_if_none(value: float | None) -> float | str:
    return "" if value is None else value


def sanitize_filename(name: str) -> str:
    """Keep generated file names inside the report directory."""
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return (cleaned or "report")[:120]


def build_row(info: Mapping[str, Any]) -> dict[str, Any]:
    """Turn a Flower task payload into a CSV row, tolerating missing fields."""
    received = _numeric(info.get("received"))
    started = _numeric(info.get("started"))
    succeeded = _numeric(info.get("succeeded"))
    return {
        "TaskUID": info.get("task-id") or info.get("uuid") or "",
        "Task": info.get("name") or "",
        "Task Received": info.get("received") if received is not None else "",
        "Task Started": info.get("started") if started is not None else "",
        "Task Succeed": info.get("succeeded") if succeeded is not None else "",
        "Runtime": info.get("runtime") if _numeric(info.get("runtime")) is not None else "",
        "Time Between Reception And Start Processing (s)": _blank_if_none(
            _suffix(started, received)
        ),
        "Processing Time (s)": _blank_if_none(_suffix(succeeded, started)),
        "Total Time(s)": _blank_if_none(_suffix(succeeded, received)),
        "WorkerName": info.get("worker") or "",
    }


class CsvReporter:
    """Append Flower task metrics to a CSV file for the lifetime of a run."""

    def __init__(self, directory: str | Path, name: str) -> None:
        self.path = Path(directory) / f"{sanitize_filename(name)}.csv"
        self._file = None
        self._writer: csv.DictWriter | None = None

    def __enter__(self) -> CsvReporter:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=FIELDS)
        self._writer.writeheader()
        return self

    def write(self, info: Mapping[str, Any]) -> None:
        if self._writer is None:
            raise RuntimeError("CsvReporter must be used as a context manager")
        self._writer.writerow(build_row(info))

    def __exit__(self, *exc_info: object) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
            self._writer = None
