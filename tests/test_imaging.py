import numpy as np
import pytest

from imageproc.imaging import (
    list_images,
    load_image,
    result_path,
    save_image,
    split_image,
)


@pytest.fixture
def image() -> np.ndarray:
    return np.arange(100, dtype=np.uint8).reshape(10, 10)


def test_save_and_load_round_trip(tmp_path, image):
    destination = tmp_path / "nested" / "result.png"
    save_image(image, destination)
    assert destination.is_file()
    assert np.array_equal(load_image(destination), image)


def test_load_rejects_missing_and_invalid_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_image(tmp_path / "missing.png")
    broken = tmp_path / "broken.png"
    broken.write_text("not an image")
    with pytest.raises(ValueError, match="decode"):
        load_image(broken)


def test_list_images_filters_and_sorts(tmp_path):
    (tmp_path / "b.png").write_bytes(b"")
    (tmp_path / "a.JPG").write_bytes(b"")
    (tmp_path / "notes.txt").write_text("ignore me")
    (tmp_path / "nested").mkdir()
    assert [path.name for path in list_images(tmp_path)] == ["a.JPG", "b.png"]


def test_list_images_requires_a_directory(tmp_path):
    with pytest.raises(NotADirectoryError):
        list_images(tmp_path / "missing")


def test_split_image_preserves_order(image):
    chunks = split_image(image, 3)
    assert len(chunks) == 3
    assert np.array_equal(np.vstack(chunks), image)


def test_split_image_handles_more_parts_than_rows(image):
    chunks = split_image(image, 20)
    assert len(chunks) == 10
    assert np.array_equal(np.vstack(chunks), image)


def test_split_image_rejects_invalid_parts(image):
    with pytest.raises(ValueError):
        split_image(image, 0)
    with pytest.raises(ValueError):
        split_image(np.array([], dtype=np.uint8), 2)


def test_result_path_keeps_extension(tmp_path):
    assert result_path(tmp_path / "photo.JPG", tmp_path / "out", "rotation") == (
        tmp_path / "out" / "photo_rotation_processed.jpg"
    )
    assert result_path(tmp_path / "photo", tmp_path / "out", "edge") == (
        tmp_path / "out" / "photo_edge_processed.png"
    )
