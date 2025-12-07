"""
S3-based data access for storing and retrieving memory JSON files.
Memory files are stored exclusively in S3, no local fallback.
"""

import json
import os
import boto3
from typing import Any
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

# Get configuration from environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "agenticai-medical-appointment-system")
S3_REGION = os.getenv("S3_REGION", "ap-south-1")

# Initialize S3 client
s3_client = None
try:
    s3_client = boto3.client('s3', region_name=S3_REGION)
    logger.info(f"S3 client initialized for bucket: {S3_BUCKET_NAME}")
except Exception as e:
    logger.error(f"Failed to initialize S3 client: {e}")
    raise RuntimeError(f"Cannot initialize S3 client. Please check AWS credentials and configuration. Error: {e}")


def load_json_file_from_s3(key: str, default: Any = None) -> Any:
    """Load JSON file from S3"""
    if not s3_client:
        raise RuntimeError("S3 client is not initialized")
    
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'NoSuchKey':
            # File doesn't exist, return default
            if default is not None:
                # Create the file in S3 with default value
                write_json_file_to_s3(key, default)
                return default
            return default
        else:
            logger.error(f"Error loading {key} from S3: {e}")
            raise
    except Exception as e:
        logger.error(f"Unexpected error loading {key} from S3: {e}")
        raise


def write_json_file_to_s3(key: str, payload: Any) -> None:
    """Write JSON file to S3"""
    if not s3_client:
        raise RuntimeError("S3 client is not initialized")
    
    try:
        json_str = json.dumps(payload, indent=2, ensure_ascii=False)
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
            Body=json_str.encode('utf-8'),
            ContentType='application/json'
        )
        logger.info(f"Successfully wrote {key} to S3")
    except Exception as e:
        logger.error(f"Error writing {key} to S3: {e}")
        raise

