"""Pure NumPy/OpenCV operations.

These functions contain no Celery or I/O code, which keeps them quick to unit
test. The Celery wrappers in :mod:`imageproc.tasks` only add (de)serialisation.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import cv2
import numpy as np

NUMBER_TYPES = (int, float, np.integer, np.floating)


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, NUMBER_TYPES):
        raise TypeError(f"{name} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _bounded(value: object, name: str, low: float, high: float, *, inclusive: bool = True) -> float:
    number = _number(value, name)
    too_low = number < low if inclusive else number <= low
    if too_low or number > high:
        cmp = "between" if inclusive else "in"
        raise ValueError(f"{name} must be {cmp} ({low}, {high}], got {number}")
    return number


def _kernel(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise TypeError(f"{name} must be an integer")
    size = int(value)
    if size <= 0 or size % 2 == 0:
        raise ValueError(f"{name} must be a positive odd integer, got {size}")
    return size


def _gray(image: np.ndarray) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    if image.ndim == 2:
        return image
    if image.ndim == 3 and image.shape[2] in (3, 4):
        code = cv2.COLOR_BGRA2GRAY if image.shape[2] == 4 else cv2.COLOR_BGR2GRAY
        return cv2.cvtColor(image, code)
    raise ValueError(f"unsupported image shape {image.shape}")


def _points(value: object, name: str) -> np.ndarray | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.split(",")
    points = np.asarray(value, dtype=np.float32)
    if points.size != 8:
        raise ValueError(f"{name} must contain four (x, y) points, got {points.size} values")
    return points.reshape(4, 2)


def edge_detection(image: np.ndarray, sigma: float = 0.33) -> np.ndarray:
    """Canny edge detection with thresholds derived from the median intensity."""
    gray = _gray(image)
    sigma = _bounded(sigma, "sigma", 0.0, 1.0, inclusive=False)
    median = float(np.median(gray))
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))
    return cv2.Canny(gray, lower, max(upper, lower + 1))


def thresholding(image: np.ndarray, threshold: int = 127, max_value: int = 255) -> np.ndarray:
    """Binary threshold; pixels above ``threshold`` become ``max_value``."""
    gray = _gray(image)
    threshold = int(_bounded(threshold, "threshold", 0, 255))
    max_value = int(_bounded(max_value, "max_value", 0, 255))
    return cv2.threshold(gray, threshold, max_value, cv2.THRESH_BINARY)[1]


def scaling(image: np.ndarray, scale_x: float = 1.0, scale_y: float | None = None) -> np.ndarray:
    """Resize by independent x/y factors."""
    if image is None or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    scale_x = _bounded(scale_x, "scale_x", 0.0, 20.0, inclusive=False)
    scale_y = (
        scale_x if scale_y is None else _bounded(scale_y, "scale_y", 0.0, 20.0, inclusive=False)
    )
    return cv2.resize(image, None, fx=scale_x, fy=scale_y, interpolation=cv2.INTER_LINEAR)


def translation(image: np.ndarray, tx: float = 0.0, ty: float = 0.0) -> np.ndarray:
    """Shift the image by ``tx``/``ty`` pixels, filling the border with black."""
    if image is None or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    tx = _number(tx, "tx")
    ty = _number(ty, "ty")
    height, width = image.shape[:2]
    matrix = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(image, matrix, (width, height))


def rotation(image: np.ndarray, angle: float = 0.0, scale: float = 1.0) -> np.ndarray:
    """Rotate around the image centre, optionally scaling."""
    if image is None or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    angle = _number(angle, "angle")
    scale = _bounded(scale, "scale", 0.0, 20.0, inclusive=False)
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, scale)
    return cv2.warpAffine(image, matrix, (width, height))


def perspective(
    image: np.ndarray,
    src: Sequence[float] | None = None,
    dst: Sequence[float] | None = None,
) -> np.ndarray:
    """Apply a four-point perspective transform.

    ``src`` and ``dst`` are four ``(x, y)`` pairs. When omitted, the image
    corners are mapped slightly inwards, which is useful as a visual demo.
    """
    if image is None or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    height, width = image.shape[:2]
    source = _points(src, "src")
    destination = _points(dst, "dst")
    if source is None:
        source = np.float32([[0, 0], [width - 1, 0], [0, height - 1], [width - 1, height - 1]])
    if destination is None:
        margin_x, margin_y = max(1, width // 20), max(1, height // 20)
        destination = np.float32(
            [
                [margin_x, margin_y],
                [width - 1 - margin_x, margin_y],
                [margin_x, height - 1 - margin_y],
                [width - 1 - margin_x, height - 1 - margin_y],
            ]
        )
    matrix = cv2.getPerspectiveTransform(source, destination)
    return cv2.warpPerspective(image, matrix, (width, height))


def smooth_average(image: np.ndarray, kernel_x: int = 5, kernel_y: int = 5) -> np.ndarray:
    """Box-filter blur."""
    if image is None or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    return cv2.blur(image, (_kernel(kernel_x, "kernel_x"), _kernel(kernel_y, "kernel_y")))


def smooth_blur(image: np.ndarray, kernel_x: int = 5, kernel_y: int = 5) -> np.ndarray:
    """Gaussian blur."""
    if image is None or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    kernel = (_kernel(kernel_x, "kernel_x"), _kernel(kernel_y, "kernel_y"))
    return cv2.GaussianBlur(image, kernel, sigmaX=0)


def laplacian(image: np.ndarray) -> np.ndarray:
    """Laplacian derivative, normalised to 8-bit so it can be saved as an image."""
    gray = _gray(image)
    return cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F))
