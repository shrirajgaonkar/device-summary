"""
Tests for FastAPI HTTP API endpoints.
"""

import sys
from pathlib import Path

# Ensure project root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_summary_success():
    """
    Test A — Successful /summary:
    Verify HTTP 200 and expected summary data structure.
    """
    response = client.get("/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["accepted"] == 3
    assert data["duplicates"] == 1
    assert len(data["errors"]) == 1
    assert data["errors"][0] == {"type": "BAD_JSON", "line": 4}

    devices = data["devices"]
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


def test_get_summary_file_failure(monkeypatch, tmp_path):
    """
    Test B — File failure:
    Verify HTTP 500 when input file cannot be read.
    """
    non_existent_file = tmp_path / "non_existent.jsonl"
    monkeypatch.setattr("app.main.DATA_FILE_PATH", non_existent_file)

    response = client.get("/summary")
    assert response.status_code == 500
    assert response.status_code != 200

    json_data = response.json()
    assert "detail" in json_data
    assert "Unable to read summary input file" in json_data["detail"]
    assert "accepted" not in json_data
