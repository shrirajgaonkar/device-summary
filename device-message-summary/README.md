# Device Message Summary API

## Overview
This project reads a JSON Lines (`.jsonl`) file containing simulated device status messages, validates and processes each record independently, detects duplicate sequence numbers, generates per-device summary metrics, and exposes the aggregated results through a FastAPI HTTP REST endpoint.

## Features
- **JSONL Processing**: Reads device messages line-by-line from a specified JSON Lines file.
- **Strict Record Validation**: Validates schema and types for `device_id`, `sequence`, and `status`.
- **Error Categorization**: Distinguishes malformed lines (`BAD_JSON`) from invalid payload structures (`INVALID_RECORD`).
- **Resilient Processing**: Continues parsing remaining records after encountering malformed or invalid lines.
- **Duplicate Detection**: Identifies duplicate records based on the `(device_id, sequence)` tuple across valid records.
- **Accepted & Duplicate Totals**: Tracks overall counts of accepted valid messages and duplicate records.
- **Per-Device Metrics**: Counts individual `ok` and `error` statuses for each valid device.
- **Out-of-Order Sequence Handling**: Determines a device's `last_status` based on its highest accepted `sequence`, regardless of line order in the file.
- **Sorted Device Output**: Formats and returns device summaries alphabetically sorted by `device_id`.
- **FastAPI REST Endpoint**: Exposes processed summary statistics at `GET /summary`.
- **Robust Error Handling**: Provides useful HTTP 500 JSON error responses when input files are missing or unreadable.

## Prerequisites
- Python 3.10 or higher
- `pip` package manager

## Setup

Set up a fresh virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

*(Note for Linux/macOS users: activate using `source .venv/bin/activate`)*

## Run Tests

Run the complete automated test suite:

```bash
pytest -q
```

Current verification result:

```text
9 passed in 0.77s
```

## Run the API

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The API will be available locally at:

http://127.0.0.1:8000

## API Usage

Request the device message summary:

`GET /summary`

URL: http://127.0.0.1:8000/summary

Example Response:

```json
{
  "accepted": 3,
  "duplicates": 1,
  "errors": [
    {
      "type": "BAD_JSON",
      "line": 4
    }
  ],
  "devices": {
    "D01": {
      "ok": 1,
      "error": 1,
      "last_sequence": 3,
      "last_status": "error"
    },
    "D02": {
      "ok": 0,
      "error": 1,
      "last_sequence": 2,
      "last_status": "error"
    }
  }
}
```

Interactive Swagger documentation is available at:

http://127.0.0.1:8000/docs

## Input Format

Every valid JSONL record must contain exactly three fields:
- `device_id`: Non-empty, non-whitespace string
- `sequence`: Integer >= 0 (booleans are strictly rejected)
- `status`: String matching `"ok"` or `"error"`

Validation rules:
- `device_id` must be a non-empty, non-whitespace string.
- `sequence` must be an integer >= 0 and cannot be boolean.
- `status` must be `"ok"` or `"error"`.
- Malformed JSON string formatting produces a `BAD_JSON` error.
- Invalid record fields or extra/missing keys produce an `INVALID_RECORD` error.
- Blank or whitespace-only lines produce a `BAD_JSON` error.

## Duplicate and Ordering Behavior

- The first valid occurrence of a `(device_id, sequence)` pair is accepted.
- Later occurrences with an already-seen `(device_id, sequence)` pair are counted as duplicates.
- Validation occurs before duplicate detection; invalid records are flagged as errors rather than duplicates.
- A duplicate record does not alter device metrics or status counts.
- The latest device status (`last_status`) is determined strictly by the highest accepted `sequence`, regardless of input arrival order.

## React Integration

- **Loading State**: Show a loading indicator/spinner while `GET /summary` request is pending.
- **Success State**: Render high-level summary cards and device status table when response is successful.
- **Empty State**: Display a dedicated "No data available" component when the API returns 0 accepted records and no devices.
- **API/Network Failure**: Display a user-friendly error banner when an HTTP 5xx error or connection error occurs.
- **Optional Retry Action**: Provide a "Retry" button to allow users to attempt refetching data after a failure.

## Assumptions

- The API processes the configured sample JSONL file from disk upon each `GET /summary` request.
- No database or persistent storage layer is required.
- Input data is synthetic and formatted as JSON Lines as required by the assignment.

## Time Spent

Approximately 2 hours, including implementation, testing, verification, and documentation.

## Unfinished Work

No unfinished work within the requested assignment scope.

## Known Limitation

The API processes the configured JSONL sample file on each request and does not persist processed results because persistence was outside the assignment scope.

## AI and Reuse Note

- AI tools were used to assist with project structure, implementation guidance, test-case design, and documentation.
- Generated suggestions/code were reviewed and adapted for the assignment requirements.
- The implementation was verified through automated tests and manual API verification.
- No private employer material, credentials, secrets, or private chat history were included.

## Project Structure

```text
device-message-summary/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── processor.py
├── data/
│   └── sample.jsonl
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_processor.py
├── .gitignore
├── pytest.ini
├── README.md
└── requirements.txt
```

## Verification

- Automated tests: 9 passed
- API `/summary`: verified
- Swagger `/docs`: verified
- Sample output: matches expected assignment result
- File-read failure handling: verified
