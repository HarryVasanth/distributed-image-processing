import base64

import numpy as np
import pytest

from imageproc.codec import decode_image, encode_image


@pytest.fixture
def gray() -> np.ndarray:
    return np.arange(64, dtype=np.uint8).reshape(8, 8)


def test_round_trip_preserves_pixels(gray):
    assert np.array_equal(decode_image(encode_image(gray)), gray)


def test_round_trip_preserves_colour():
    image = np.zeros((5, 7, 3), dtype=np.uint8)
    image[0, 0] = (1, 2, 3)
    assert np.array_equal(decode_image(encode_image(image)), image)


def test_empty_image_is_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        encode_image(np.array([], dtype=np.uint8))


@pytest.mark.parametrize("payload", ["", "not base64!", base64.b64encode(b"hello").decode()])
def test_invalid_payloads_are_rejected(payload):
    with pytest.raises(ValueError):
        decode_image(payload)


def test_non_string_payload_is_rejected():
    with pytest.raises(ValueError):
        decode_image(None)  # type: ignore[arg-type]
