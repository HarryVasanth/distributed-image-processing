import numpy as np
import pytest

from imageproc import operations


@pytest.fixture
def gray() -> np.ndarray:
    image = np.zeros((40, 60), dtype=np.uint8)
    image[10:30, 20:40] = 255
    return image


@pytest.fixture
def colour() -> np.ndarray:
    image = np.zeros((30, 50, 3), dtype=np.uint8)
    image[:, :25] = (255, 0, 0)
    return image


def test_edge_detection(gray):
    result = operations.edge_detection(gray)
    assert result.shape == gray.shape
    assert result.dtype == np.uint8
    assert result.any()


def test_thresholding_is_binary(gray):
    result = operations.thresholding(gray, threshold=100, max_value=255)
    assert result.shape == gray.shape
    assert set(np.unique(result)).issubset({0, 255})


def test_colour_images_are_converted_for_gray_operations(colour):
    assert operations.thresholding(colour).ndim == 2
    assert operations.edge_detection(colour).ndim == 2
    assert operations.laplacian(colour).ndim == 2


def test_scaling(gray):
    result = operations.scaling(gray, scale_x=2.0, scale_y=0.5)
    assert result.shape == (gray.shape[0] // 2, gray.shape[1] * 2)


def test_scaling_can_infer_y_from_x(gray):
    result = operations.scaling(gray, scale_x=0.5)
    assert result.shape == (20, 30)


def test_translation(gray):
    result = operations.translation(gray, tx=5, ty=3)
    assert result.shape == gray.shape
    assert result.dtype == np.uint8


def test_rotation(gray):
    result = operations.rotation(gray, angle=45, scale=0.5)
    assert result.shape == gray.shape
    assert result.dtype == np.uint8


def test_perspective_default_and_explicit_points(gray):
    default = operations.perspective(gray)
    explicit = operations.perspective(gray, src=[0, 0, 59, 0, 0, 39, 59, 39])
    assert default.shape == gray.shape
    assert explicit.shape == gray.shape


def test_blur_variants(gray):
    average = operations.smooth_average(gray, kernel_x=3, kernel_y=5)
    gaussian = operations.smooth_blur(gray, kernel_x=5, kernel_y=3)
    assert average.shape == gray.shape
    assert gaussian.shape == gray.shape
    assert not np.array_equal(average, gray)
    assert not np.array_equal(gaussian, gray)


def test_laplacian_returns_8_bit(gray):
    result = operations.laplacian(gray)
    assert result.shape == gray.shape
    assert result.dtype == np.uint8


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda: operations.edge_detection(np.zeros((10, 10), np.uint8), sigma=0), "sigma"),
        (lambda: operations.thresholding(np.zeros((10, 10), np.uint8), threshold=300), "threshold"),
        (lambda: operations.scaling(np.zeros((10, 10), np.uint8), scale_x=0), "scale_x"),
        (lambda: operations.smooth_average(np.zeros((10, 10), np.uint8), kernel_x=4), "kernel_x"),
        (lambda: operations.smooth_blur(np.zeros((10, 10), np.uint8), kernel_y=-1), "kernel_y"),
    ],
)
def test_invalid_parameters_are_rejected(call, message):
    with pytest.raises((TypeError, ValueError), match=message):
        call()


def test_unsupported_and_empty_images_are_rejected():
    with pytest.raises(ValueError):
        operations.edge_detection(np.zeros((0, 0), np.uint8))
    with pytest.raises(ValueError):
        operations.edge_detection(np.zeros((4, 4, 2), np.uint8))


def test_input_is_not_mutated(gray):
    before = gray.copy()
    operations.translation(gray, tx=4, ty=2)
    assert np.array_equal(gray, before)
