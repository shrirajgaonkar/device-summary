"""
Main FastAPI application entry point.
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from app.processor import process_messages

app = FastAPI(
    title="Device Message Summary API",
    description="API to serve summary reports of processed device messages.",
    version="0.1.0",
)

# Default path to sample JSONL file
DATA_FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample.jsonl"


@app.get("/")
def read_root():
    return {"message": "Device Message Summary API is running"}


@app.get("/summary")
def get_summary():
    """
    Process sample device messages JSONL file and return summary.
    """
    try:
        return process_messages(DATA_FILE_PATH)
    except (FileNotFoundError, OSError, Exception) as err:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read summary input file: {err}",
        )
