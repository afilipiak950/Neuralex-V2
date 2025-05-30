"""
async def predict(job_payload: dict) -> dict:
    POST http://ML_SERVER/predict
    Rückgabe JSON {doc_type,event_type,entities}

TODO: Add retry-logic in ml_client.predict()
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import asyncio

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# ML Server Configuration
ML_SERVER_URL = os.getenv("ML_SERVER_URL", "http://localhost:8000")
ML_API_KEY = os.getenv("ML_API_KEY", "default_key")
REQUEST_TIMEOUT = int(os.getenv("ML_REQUEST_TIMEOUT", "30"))

class MLClientError(Exception):
    """Custom exception for ML client errors"""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
async def predict_document(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send document to ML server for prediction
    
    Args:
        payload: Document data to classify
        
    Returns:
        Dict containing prediction results:
        {
            "doc_type": str,
            "event_type": str,
            "confidence": float,
            "entities": [
                {
                    "type": str,
                    "text": str,
                    "confidence": float,
                    "start_pos": int,
                    "end_pos": int
                }
            ]
        }
        
    Raises:
        MLClientError: If prediction fails
    """
    try:
        logger.info(f"Sending prediction request to ML server: {ML_SERVER_URL}")
        
        # Prepare request data
        request_data = {
            "text": _extract_text_from_payload(payload),
            "metadata": payload.get("metadata", {}),
            "options": {
                "include_entities": True,
                "include_confidence": True
            }
        }
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ML_API_KEY}",
            "User-Agent": "NeuraLex-Platform/1.0"
        }
        
        # Make async HTTP request
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{ML_SERVER_URL}/predict",
                json=request_data,
                headers=headers
            )
            
            # Check response status
            if response.status_code != 200:
                error_msg = f"ML server error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise MLClientError(error_msg)
            
            # Parse response
            result = response.json()
            
            # Validate response structure
            validated_result = _validate_prediction_response(result)
            
            logger.info("Successfully received prediction from ML server")
            return validated_result
            
    except httpx.TimeoutException:
        error_msg = f"ML server timeout after {REQUEST_TIMEOUT} seconds"
        logger.error(error_msg)
        raise MLClientError(error_msg)
        
    except httpx.RequestError as e:
        error_msg = f"ML server connection error: {e}"
        logger.error(error_msg)
        raise MLClientError(error_msg)
        
    except Exception as e:
        error_msg = f"ML prediction failed: {e}"
        logger.error(error_msg)
        raise MLClientError(error_msg)

def _extract_text_from_payload(payload: Dict[str, Any]) -> str:
    """Extract text content from various payload formats"""
    
    # Direct text field
    if "text" in payload:
        return str(payload["text"])
    
    # Content field
    if "content" in payload:
        return str(payload["content"])
    
    # Body field
    if "body" in payload:
        return str(payload["body"])
    
    # Message field
    if "message" in payload:
        return str(payload["message"])
    
    # Document field with text
    if "document" in payload and isinstance(payload["document"], dict):
        doc = payload["document"]
        if "text" in doc:
            return str(doc["text"])
        if "content" in doc:
            return str(doc["content"])
    
    # Try to extract from nested structures
    for key, value in payload.items():
        if isinstance(value, str) and len(value) > 10:  # Likely text content
            return value
    
    # Fallback: serialize entire payload as text
    return json.dumps(payload, indent=2)

def _validate_prediction_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize prediction response"""
    
    # Ensure required fields exist
    validated = {
        "doc_type": response.get("doc_type", "unknown"),
        "event_type": response.get("event_type", "unknown"),
        "confidence": float(response.get("confidence", 0.0)),
        "entities": []
    }
    
    # Validate confidence score
    if not 0.0 <= validated["confidence"] <= 1.0:
        validated["confidence"] = 0.0
    
    # Process entities
    entities = response.get("entities", [])
    if isinstance(entities, list):
        for entity in entities:
            if isinstance(entity, dict):
                validated_entity = {
                    "type": entity.get("type", "unknown"),
                    "text": entity.get("text", ""),
                    "confidence": float(entity.get("confidence", 0.0)),
                    "start_pos": int(entity.get("start_pos", 0)),
                    "end_pos": int(entity.get("end_pos", 0))
                }
                
                # Validate entity confidence
                if not 0.0 <= validated_entity["confidence"] <= 1.0:
                    validated_entity["confidence"] = 0.0
                
                validated["entities"].append(validated_entity)
    
    return validated

async def health_check() -> bool:
    """Check if ML server is available"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{ML_SERVER_URL}/health")
            return response.status_code == 200
    except Exception:
        return False

async def get_server_info() -> Optional[Dict[str, Any]]:
    """Get information about the ML server"""
    try:
        headers = {
            "Authorization": f"Bearer {ML_API_KEY}",
            "User-Agent": "NeuraLex-Platform/1.0"
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{ML_SERVER_URL}/info",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            
    except Exception as e:
        logger.error(f"Failed to get server info: {e}")
    
    return None

# Fallback prediction for testing
async def predict_document_fallback(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback prediction method for testing when ML server is not available
    Returns mock prediction data
    """
    logger.warning("Using fallback prediction mode")
    
    text = _extract_text_from_payload(payload)
    
    # Simple heuristic-based classification for testing
    doc_type = "document"
    event_type = "general"
    confidence = 0.75
    
    if "invoice" in text.lower():
        doc_type = "invoice"
        event_type = "billing"
        confidence = 0.85
    elif "contract" in text.lower():
        doc_type = "contract"
        event_type = "legal"
        confidence = 0.80
    elif "email" in text.lower():
        doc_type = "email"
        event_type = "communication"
        confidence = 0.70
    
    # Mock entities
    entities = []
    if "@" in text:
        entities.append({
            "type": "email",
            "text": "example@example.com",
            "confidence": 0.9,
            "start_pos": text.find("@") - 5,
            "end_pos": text.find("@") + 10
        })
    
    return {
        "doc_type": doc_type,
        "event_type": event_type,
        "confidence": confidence,
        "entities": entities
    }
