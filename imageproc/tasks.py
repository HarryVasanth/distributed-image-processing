"""Celery task wrappers around :mod:`imageproc.operations`.

Every task accepts and returns a base64 PNG payload so the whole pipeline can
use Celery's JSON serialiser safely.
"""

from __future__ import annotations

from celery.utils.log import get_task_logger

from . import operations
from .celery_app import app
from .codec import decode_image, encode_image

logger = get_task_logger(__name__)


def _run(name: str, func, payload: str, **params):
    logger.info("running %s", name)
    return encode_image(func(decode_image(payload), **params))


@app.task(name="imageproc.edge_detection")
def edge_detection(payload: str, sigma: float = 0.33) -> str:
    return _run("edge_detection", operations.edge_detection, payload, sigma=sigma)


@app.task(name="imageproc.thresholding")
def thresholding(payload: str, threshold: int = 127, max_value: int = 255) -> str:
    return _run(
        "thresholding",
        operations.thresholding,
        payload,
        threshold=threshold,
        max_value=max_value,
    )


@app.task(name="imageproc.scaling")
def scaling(payload: str, scale_x: float = 1.0, scale_y: float | None = None) -> str:
    return _run("scaling", operations.scaling, payload, scale_x=scale_x, scale_y=scale_y)


@app.task(name="imageproc.translation")
def translation(payload: str, tx: float = 0.0, ty: float = 0.0) -> str:
    return _run("translation", operations.translation, payload, tx=tx, ty=ty)


@app.task(name="imageproc.rotation")
def rotation(payload: str, angle: float = 0.0, scale: float = 1.0) -> str:
    return _run("rotation", operations.rotation, payload, angle=angle, scale=scale)


@app.task(name="imageproc.perspective")
def perspective(payload: str, src=None, dst=None) -> str:
    return _run("perspective", operations.perspective, payload, src=src, dst=dst)


@app.task(name="imageproc.smooth_average")
def smooth_average(payload: str, kernel_x: int = 5, kernel_y: int = 5) -> str:
    return _run(
        "smooth_average",
        operations.smooth_average,
        payload,
        kernel_x=kernel_x,
        kernel_y=kernel_y,
    )


@app.task(name="imageproc.smooth_blur")
def smooth_blur(payload: str, kernel_x: int = 5, kernel_y: int = 5) -> str:
    return _run(
        "smooth_blur",
        operations.smooth_blur,
        payload,
        kernel_x=kernel_x,
        kernel_y=kernel_y,
    )


@app.task(name="imageproc.laplacian")
def laplacian(payload: str) -> str:
    return _run("laplacian", operations.laplacian, payload)
