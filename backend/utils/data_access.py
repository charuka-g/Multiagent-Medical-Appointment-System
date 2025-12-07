"""
Data access module for JSON files.
All files are stored exclusively in S3 - no local filesystem support.
"""

from typing import Any
import logging

logger = logging.getLogger(__name__)

# Import S3 data access functions
try:
    from utils.s3_data_access import (
        load_json_file_from_s3,
        write_json_file_to_s3
    )
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    logger.error("S3 data access not available. Cannot load/write files.")


def load_json_file(filename: str, default: Any = None) -> Any:
    """
    Load a JSON file from S3.
    All files are stored exclusively in S3 - no local filesystem support.
    """
    if not S3_AVAILABLE:
        raise RuntimeError(
            f"Cannot load {filename}: S3 storage is required. "
            "Please ensure S3 is configured with AWS credentials."
        )
    return load_json_file_from_s3(filename, default)


def write_json_file(filename: str, payload: Any) -> None:
    """
    Write a JSON file to S3.
    All files are stored exclusively in S3 - no local filesystem support.
    """
    if not S3_AVAILABLE:
        raise RuntimeError(
            f"Cannot write {filename}: S3 storage is required. "
            "Please ensure S3 is configured with AWS credentials."
        )
    write_json_file_to_s3(filename, payload)
