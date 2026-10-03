import json
from pathlib import Path
from typing import Any, Dict, List, Union


def process_messages(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read a JSON Lines (.jsonl) file containing simulated device messages,
    validate each line, and return a summary report.
    """
    path = Path(file_path)

    accepted_count = 0
    duplicate_count = 0
    errors: List[Dict[str, Any]] = []
    seen_pairs = set()
    devices: Dict[str, Dict[str, Any]] = {}

    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                errors.append({"type": "BAD_JSON", "line": line_num})
                continue

            try:
                record = json.loads(line)
            except Exception:
                errors.append({"type": "BAD_JSON", "line": line_num})
                continue

            if not isinstance(record, dict):
                errors.append({"type": "INVALID_RECORD", "line": line_num})
                continue

            if set(record.keys()) != {"device_id", "sequence", "status"}:
                errors.append({"type": "INVALID_RECORD", "line": line_num})
                continue

            device_id = record["device_id"]
            sequence = record["sequence"]
            status = record["status"]

            # Validation rules:
            # - device_id must be a non-empty string and not whitespace-only
            if not isinstance(device_id, str) or len(device_id) == 0 or not device_id.strip():
                errors.append({"type": "INVALID_RECORD", "line": line_num})
                continue

            # - sequence must be an integer >= 0 (booleans excluded)
            if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
                errors.append({"type": "INVALID_RECORD", "line": line_num})
                continue

            # - status must be "ok" or "error"
            if status not in ("ok", "error"):
                errors.append({"type": "INVALID_RECORD", "line": line_num})
                continue

            # Duplicate check after record validation
            pair = (device_id, sequence)
            if pair in seen_pairs:
                duplicate_count += 1
                continue

            seen_pairs.add(pair)
            accepted_count += 1

            if device_id not in devices:
                devices[device_id] = {
                    "ok": 1 if status == "ok" else 0,
                    "error": 1 if status == "error" else 0,
                    "last_sequence": sequence,
                    "last_status": status,
                }
            else:
                if status == "ok":
                    devices[device_id]["ok"] += 1
                else:
                    devices[device_id]["error"] += 1

                if sequence > devices[device_id]["last_sequence"]:
                    devices[device_id]["last_sequence"] = sequence
                    devices[device_id]["last_status"] = status

    return {
        "accepted": accepted_count,
        "duplicates": duplicate_count,
        "errors": errors,
        "devices": dict(sorted(devices.items())),
    }

