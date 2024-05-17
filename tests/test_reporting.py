import csv

from imageproc.reporting import FIELDS, CsvReporter, build_row, sanitize_filename


def test_build_row_computes_durations():
    row = build_row(
        {
            "task-id": "abc",
            "name": "imageproc.edge_detection",
            "received": 10.0,
            "started": 12.5,
            "succeeded": 13.0,
            "runtime": 0.5,
            "worker": "worker-1",
        }
    )
    assert row["TaskUID"] == "abc"
    assert row["Time Between Reception And Start Processing (s)"] == 2.5
    assert row["Processing Time (s)"] == 0.5
    assert row["Total Time(s)"] == 3.0
    assert row["WorkerName"] == "worker-1"


def test_build_row_keeps_zero_durations():
    row = build_row({"received": 1.0, "started": 1.0, "succeeded": 1.0})
    assert row["Processing Time (s)"] == 0.0


def test_build_row_tolerates_missing_fields():
    row = build_row({})
    assert row["TaskUID"] == ""
    assert row["Task Received"] == ""
    assert row["Total Time(s)"] == ""


def test_reporter_writes_header_and_rows(tmp_path):
    with CsvReporter(tmp_path, "metrics") as reporter:
        reporter.write({"task-id": "one", "received": 1.0, "started": 2.0, "succeeded": 3.0})
        reporter.write({"task-id": "two"})

    with (tmp_path / "metrics.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert list(rows[0]) == FIELDS
    assert [row["TaskUID"] for row in rows] == ["one", "two"]


def test_reporter_requires_context_manager(tmp_path):
    reporter = CsvReporter(tmp_path, "metrics")
    try:
        reporter.write({})
    except RuntimeError as exc:
        assert "context manager" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("write outside a context manager should fail")


def test_sanitize_filename_stays_inside_directory():
    assert sanitize_filename("../../etc/passwd") == "etc_passwd"
    assert sanitize_filename("") == "report"
    assert sanitize_filename("a" * 200) == "a" * 120
