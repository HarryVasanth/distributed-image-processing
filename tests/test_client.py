from dataclasses import replace

import numpy as np
import pytest

import imageproc.client as client_module
from imageproc.client import (
    ALGORITHMS,
    Algorithm,
    ProcessingClient,
    ProcessingError,
    _as_points,
    parse_params,
)


class FakeAsyncResult:
    def __init__(self, payload=None, error=None, ready=True):
        self.id = "task-1"
        self._payload = payload
        self._error = error
        self._ready = ready
        self.revoked = False

    def ready(self):
        return self._ready

    def get(self, propagate=True):
        if self._error:
            raise RuntimeError(self._error)
        return self._payload

    def revoke(self):
        self.revoked = True


class EchoTask:
    def delay(self, payload, **params):
        return FakeAsyncResult(payload)


def _echo_algorithm(*, split=True):
    return Algorithm("echo", EchoTask(), "echo", supports_split=split)


@pytest.fixture
def image():
    return np.arange(120, dtype=np.uint8).reshape(12, 10)


def test_parse_params_uses_defaults():
    assert parse_params(ALGORITHMS["edge_detection"], []) == {"sigma": 0.33}
    assert parse_params(ALGORITHMS["laplacian"], []) == {}


def test_parse_params_casts_overrides():
    params = parse_params(ALGORITHMS["thresholding"], ["threshold=10", "max_value=200"])
    assert params == {"threshold": 10, "max_value": 200}


def test_parse_params_parses_points():
    params = parse_params(ALGORITHMS["perspective"], ["src=0,0,1,0,0,1,1,1", "dst=0,0,2,0,0,2,2,2"])
    assert params["src"] == [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0]


def test_parse_params_rejects_unknown_and_bad_values():
    with pytest.raises(ValueError, match="unknown parameter"):
        parse_params(ALGORITHMS["edge_detection"], ["nope=1"])
    with pytest.raises(ValueError, match="expected NAME=VALUE"):
        parse_params(ALGORITHMS["edge_detection"], ["sigma"])
    with pytest.raises(ValueError, match="invalid value"):
        parse_params(ALGORITHMS["thresholding"], ["threshold=abc"])


def test_as_points_accepts_strings_and_sequences():
    assert _as_points("0,0,1,0,0,1,1,1") == [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0]
    assert _as_points([0, 0, 1, 0, 0, 1, 1, 1]) == [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0]
    with pytest.raises(ValueError, match="eight"):
        _as_points("0,0,1,1")


def test_process_merges_split_chunks(monkeypatch, image):
    monkeypatch.setattr(client_module, "settings", replace(client_module.settings, chunks=3))
    with ProcessingClient() as client:
        output = client.process(image, _echo_algorithm())
    assert np.array_equal(output, image)


def test_process_without_split_returns_a_single_result(image):
    with ProcessingClient() as client:
        output = client.process(image, _echo_algorithm(split=False), split=False)
    assert np.array_equal(output, image)


def test_process_rejects_split_for_unsupported_algorithms(image):
    with ProcessingClient() as client, pytest.raises(ValueError, match="does not support"):
        client.process(image, _echo_algorithm(split=False), split=True)


def test_worker_failure_becomes_processing_error(image):
    class FailingTask:
        def delay(self, payload, **params):
            return FakeAsyncResult(error="worker exploded")

    with ProcessingClient() as client, pytest.raises(ProcessingError, match="failed"):
        client.process(image, Algorithm("fail", FailingTask(), "", supports_split=False))


def test_timeout_revokes_pending_tasks(image):
    class HangingTask:
        def __init__(self):
            self.results = []

        def delay(self, payload, **params):
            result = FakeAsyncResult(ready=False)
            self.results.append(result)
            return result

    task = HangingTask()
    with ProcessingClient(timeout=0.01, poll_interval=0.001) as client, pytest.raises(TimeoutError):
        client.process(image, Algorithm("hang", task, "", supports_split=False))
    assert all(result.revoked for result in task.results)


def test_flower_url_must_be_http():
    with pytest.raises(ValueError, match="http"):
        ProcessingClient(flower_url="file:///etc/passwd")


def test_registry_tasks_are_unique_and_named():
    names = [algorithm.name for algorithm in ALGORITHMS.values()]
    assert len(names) == len(set(names))
    assert all(algorithm.task.name.startswith("imageproc.") for algorithm in ALGORITHMS.values())
