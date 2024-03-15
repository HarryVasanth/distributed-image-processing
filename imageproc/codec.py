"""PNG/base64 codec used to move images through the JSON task protocol."""

from __future__ import annotations

import base64
import binascii

import cv2
import numpy as np

from .config import settings


def encode_image(image: np.ndarray) -> str:
    """Serialise an image as a base64 PNG string.

    Raises:
        ValueError: if the input is empty or cannot be encoded.
    """
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("image must be a non-empty numpy array")
    ok, buffer = cv2.imencode(".png", image)
    if not ok:
        raise ValueError("OpenCV could not encode the image as PNG")
    return base64.b64encode(buffer.tobytes()).decode("ascii")


def decode_image(payload: str) -> np.ndarray:
    """Decode a base64 PNG string back into an image.

    Raises:
        ValueError: if the payload is empty, too large, not base64 or not an image.
    """
    if not isinstance(payload, str) or not payload:
        raise ValueError("image payload must be a non-empty string")
    # base64 grows data by ~4/3; reject early so a hostile payload cannot allocate RAM.
    if len(payload) > settings.max_payload_bytes * 4 // 3 + 4:
        raise ValueError("image payload exceeds IMAGEPROC_MAX_PAYLOAD_BYTES")
    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("image payload is not valid base64") from exc
    if len(raw) > settings.max_payload_bytes:
        raise ValueError("image payload exceeds IMAGEPROC_MAX_PAYLOAD_BYTES")
    image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if image is None or image.size == 0:
        raise ValueError("payload does not contain a decodable image")
    return image
