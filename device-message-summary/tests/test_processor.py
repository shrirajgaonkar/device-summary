import json
from pathlib import Path
import pytest
from app.processor import process_messages

SAMPLE_JSONL_PATH = Path(__file__).parent.parent / "data" / "sample.jsonl"


def test_sample_jsonl():
    """
    TEST 1 — Sample:
    Use the supplied sample JSONL and verify requirements.
    """
    result = process_messages(SAMPLE_JSONL_PATH)

    assert result["accepted"] == 3
    assert result["duplicates"] == 1
    assert len(result["errors"]) == 1
    assert result["errors"][0] == {"type": "BAD_JSON", "line": 4}

    devices = result["devices"]
    assert "D01" in devices
    assert devices["D01"] == {
        "ok": 1,
        "error": 1,
        "last_sequence": 3,
        "last_status": "error",
    }

    assert "D02" in devices
    assert devices["D02"] == {
        "ok": 0,
        "error": 1,
        "last_sequence": 2,
        "last_status": "error",
    }


def test_out_of_order_sequence(tmp_path):
    """
    TEST 2 — Out-of-order sequence:
    Higher sequence arrives before lower sequence.
    """
    test_file = tmp_path / "out_of_order.jsonl"
    lines = [
        {"device_id": "D01", "sequence": 5, "status": "error"},
        {"device_id": "D01", "sequence": 2, "status": "ok"},
    ]
    test_file.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")

    result = process_messages(test_file)

    assert result["accepted"] == 2
    assert result["devices"]["D01"]["last_sequence"] == 5
    assert result["devices"]["D01"]["last_status"] == "error"
    assert result["devices"]["D01"]["ok"] == 1
    assert result["devices"]["D01"]["error"] == 1


def test_empty_input(tmp_path):
    """
    TEST 3 — Empty input:
    Returns standard empty result dict.
    """
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("", encoding="utf-8")

    result = process_messages(empty_file)

    assert result == {
        "accepted": 0,
        "duplicates": 0,
        "errors": [],
        "devices": {},
    }


def test_malformed_json(tmp_path):
    """
    Edge case: Malformed JSON and blank lines.
    """
    file_path = tmp_path / "malformed.jsonl"
    content = "not json\n\n{\"device_id\": \"D01\", \"sequence\": 1, \"status\": \"ok\"}\n"
    file_path.write_text(content, encoding="utf-8")

    result = process_messages(file_path)

    assert result["accepted"] == 1
    assert result["errors"] == [
        {"type": "BAD_JSON", "line": 1},
        {"type": "BAD_JSON", "line": 2},
    ]


def test_invalid_records(tmp_path):
    """
    Edge cases: invalid status, negative sequence, boolean sequence,
    missing field, extra field, whitespace-only device_id.
    """
    file_path = tmp_path / "invalid_records.jsonl"
    records = [
        {"device_id": "D01", "sequence": 1, "status": "invalid_status"},  # invalid status
        {"device_id": "D01", "sequence": -1, "status": "ok"},  # negative sequence
        {"device_id": "D01", "sequence": True, "status": "ok"},  # boolean sequence
        {"device_id": "D01", "sequence": 1},  # missing field
        {"device_id": "D01", "sequence": 1, "status": "ok", "extra": "field"},  # extra field
        {"device_id": "   ", "sequence": 1, "status": "ok"},  # whitespace-only device_id
        {"device_id": "", "sequence": 1, "status": "ok"},  # empty device_id
    ]
    file_path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

    result = process_messages(file_path)

    assert result["accepted"] == 0
    assert len(result["errors"]) == 7
    for err in result["errors"]:
        assert err["type"] == "INVALID_RECORD"


def test_duplicate_with_different_status(tmp_path):
    """
    Edge case: Duplicate (device_id, sequence) with different status.
    Must be counted as duplicate and not affect device stats.
    """
    file_path = tmp_path / "duplicates.jsonl"
    lines = [
        {"device_id": "D01", "sequence": 1, "status": "ok"},
        {"device_id": "D01", "sequence": 1, "status": "error"},
    ]
    file_path.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")

    result = process_messages(file_path)

    assert result["accepted"] == 1
    assert result["duplicates"] == 1
    assert result["devices"]["D01"] == {
        "ok": 1,
        "error": 0,
        "last_sequence": 1,
        "last_status": "ok",
    }


def test_file_not_found():
    """
    File reading errors raise FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        process_messages("non_existent_file.jsonl")
