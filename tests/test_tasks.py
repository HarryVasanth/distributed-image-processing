import numpy as np

from imageproc import tasks
from imageproc.codec import decode_image, encode_image


def test_edge_detection_task_round_trip():
    image = np.tile(np.arange(0, 200, 5, dtype=np.uint8), (20, 1))
    result = decode_image(tasks.edge_detection.run(encode_image(image)))
    assert result.shape == image.shape
    assert result.dtype == np.uint8


def test_all_tasks_accept_encoded_images():
    image = np.full((16, 16), 100, dtype=np.uint8)
    payload = encode_image(image)
    cases = {
        tasks.edge_detection: {},
        tasks.thresholding: {"threshold": 50},
        tasks.scaling: {"scale_x": 2.0},
        tasks.translation: {"tx": 2, "ty": 2},
        tasks.rotation: {"angle": 10},
        tasks.perspective: {},
        tasks.smooth_average: {"kernel_x": 3, "kernel_y": 3},
        tasks.smooth_blur: {"kernel_x": 3, "kernel_y": 3},
        tasks.laplacian: {},
    }
    for task, params in cases.items():
        result = decode_image(task.run(payload, **params))
        assert result.size > 0
        assert result.dtype == np.uint8
