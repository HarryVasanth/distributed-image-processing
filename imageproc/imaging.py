"""Image loading, splitting and result persistence."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

IMAGE_EXTENSIONS = frozenset({".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"})


def load_image(path: str | Path, flags: int = cv2.IMREAD_GRAYSCALE) -> np.ndarray:
    """Load an image, raising a useful error instead of returning ``None``."""
    source = Path(path).expanduser()
    if not source.is_file():
        raise FileNotFoundError(f"image not found: {source}")
    image = cv2.imread(str(source), flags)
    if image is None or image.size == 0:
        raise ValueError(f"could not decode image: {source}")
    return image


def list_images(folder: str | Path) -> list[Path]:
    """Return supported image files directly inside ``folder``, sorted by name."""
    root = Path(folder).expanduser()
    if not root.is_dir():
        raise NotADirectoryError(f"image folder not found: {root}")
    return sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def split_image(image: np.ndarray, parts: int) -> list[np.ndarray]:
    """Split an image into at most ``parts`` horizontal strips."""
    if not isinstance(parts, int) or parts <= 0:
        raise ValueError("parts must be a positive integer")
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    return [chunk for chunk in np.array_split(image, parts, axis=0) if chunk.size]


def result_path(source: str | Path, results_dir: str | Path, algorithm: str) -> Path:
    """Build ``<results_dir>/<stem>_<algorithm>_processed<ext>`` for a source image."""
    source = Path(source)
    suffix = source.suffix.lower() or ".png"
    return Path(results_dir) / f"{source.stem}_{algorithm}_processed{suffix}"


def save_image(image: np.ndarray, destination: str | Path) -> Path:
    """Write an image, creating parent directories and verifying the write."""
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise OSError(f"could not write image: {path}")
    return path
