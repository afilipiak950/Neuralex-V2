"""
fetch(gcs_uri) -> dict
Verwendet google-cloud-storage-Client (place holder für creds).
"""

import os
import json
import logging
from typing import Dict, Any, Optional

import aiohttp
from google.cloud import storage
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

# GCP Configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "neuralex-incoming-json")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")

async def fetch_from_gcs(gcs_uri: str) -> Dict[str, Any]:
    """
    Fetch document content from Google Cloud Storage
    
    Args:
        gcs_uri: GCS URI in format gs://bucket-name/path/to/file.json
        
    Returns:
        Dict containing the document content
        
    Raises:
        Exception: If fetch fails
    """
    try:
        logger.info(f"Fetching document from GCS: {gcs_uri}")
        
        # Parse GCS URI
        if not gcs_uri.startswith("gs://"):
            raise ValueError("Invalid GCS URI format. Must start with gs://")
        
        # Remove gs:// prefix and split bucket/path
        uri_parts = gcs_uri[5:].split("/", 1)
        if len(uri_parts) != 2:
            raise ValueError("Invalid GCS URI format. Must be gs://bucket/path")
        
        bucket_name, blob_path = uri_parts
        
        # Initialize GCS client
        if GCP_CREDENTIALS_PATH and os.path.exists(GCP_CREDENTIALS_PATH):
            credentials = service_account.Credentials.from_service_account_file(
                GCP_CREDENTIALS_PATH
            )
            client = storage.Client(credentials=credentials)
        else:
            # Use default credentials (for cloud environments)
            client = storage.Client()
        
        # Get bucket and blob
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        # Check if blob exists
        if not blob.exists():
            raise FileNotFoundError(f"File not found in GCS: {gcs_uri}")
        
        # Download and parse content
        content = blob.download_as_text()
        
        # Try to parse as JSON
        try:
            document_data = json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, return as text content
            document_data = {"text": content, "content_type": "text/plain"}
        
        logger.info(f"Successfully fetched document from GCS: {gcs_uri}")
        return document_data
        
    except Exception as e:
        logger.error(f"Failed to fetch from GCS {gcs_uri}: {e}")
        raise Exception(f"GCS fetch failed: {e}")

async def list_bucket_objects(bucket_name: Optional[str] = None, prefix: str = "") -> list:
    """
    List objects in a GCS bucket
    
    Args:
        bucket_name: Name of the bucket (defaults to configured bucket)
        prefix: Prefix to filter objects
        
    Returns:
        List of object names
    """
    try:
        bucket_name = bucket_name or GCP_BUCKET_NAME
        
        # Initialize GCS client
        if GCP_CREDENTIALS_PATH and os.path.exists(GCP_CREDENTIALS_PATH):
            credentials = service_account.Credentials.from_service_account_file(
                GCP_CREDENTIALS_PATH
            )
            client = storage.Client(credentials=credentials)
        else:
            client = storage.Client()
        
        bucket = client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        
        return [blob.name for blob in blobs]
        
    except Exception as e:
        logger.error(f"Failed to list bucket objects: {e}")
        raise Exception(f"Bucket listing failed: {e}")

async def upload_to_gcs(data: Dict[str, Any], destination_path: str, 
                       bucket_name: Optional[str] = None) -> str:
    """
    Upload data to Google Cloud Storage
    
    Args:
        data: Data to upload (will be JSON serialized)
        destination_path: Path within the bucket
        bucket_name: Name of the bucket (defaults to configured bucket)
        
    Returns:
        GCS URI of the uploaded file
    """
    try:
        bucket_name = bucket_name or GCP_BUCKET_NAME
        
        # Initialize GCS client
        if GCP_CREDENTIALS_PATH and os.path.exists(GCP_CREDENTIALS_PATH):
            credentials = service_account.Credentials.from_service_account_file(
                GCP_CREDENTIALS_PATH
            )
            client = storage.Client(credentials=credentials)
        else:
            client = storage.Client()
        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_path)
        
        # Upload JSON data
        json_data = json.dumps(data, indent=2)
        blob.upload_from_string(json_data, content_type="application/json")
        
        gcs_uri = f"gs://{bucket_name}/{destination_path}"
        logger.info(f"Uploaded data to GCS: {gcs_uri}")
        
        return gcs_uri
        
    except Exception as e:
        logger.error(f"Failed to upload to GCS: {e}")
        raise Exception(f"GCS upload failed: {e}")

# Async wrapper for testing without actual GCS (fallback mode)
async def fetch_from_gcs_fallback(gcs_uri: str) -> Dict[str, Any]:
    """
    Fallback fetch method for testing when GCS is not available
    Returns sample data structure
    """
    logger.warning(f"Using fallback mode for GCS fetch: {gcs_uri}")
    
    # Return a sample document structure
    return {
        "text": "Sample document content for testing",
        "metadata": {
            "source": gcs_uri,
            "timestamp": "2024-01-01T00:00:00Z",
            "content_type": "application/json"
        },
        "properties": {
            "language": "en",
            "length": 100
        }
    }
