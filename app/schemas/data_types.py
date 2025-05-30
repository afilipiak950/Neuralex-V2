"""
Pydantic schemas for core data types
Generated from dataTypes.json schema
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
import uuid

class IngestRequest(BaseModel):
    """Request schema for document ingestion"""
    gcs_uri: Optional[str] = Field(None, description="GCS URI for document to process")
    payload: Optional[Dict[str, Any]] = Field(None, description="Direct document payload")
    
    @validator('gcs_uri')
    def validate_gcs_uri(cls, v):
        if v is not None and not v.startswith('gs://'):
            raise ValueError('GCS URI must start with gs://')
        return v
    
    @validator('payload')
    def validate_payload_or_uri(cls, v, values):
        if v is None and values.get('gcs_uri') is None:
            raise ValueError('Either gcs_uri or payload must be provided')
        return v

class IngestResponse(BaseModel):
    """Response schema for document ingestion"""
    job_id: str = Field(description="Unique job identifier")
    status: str = Field(description="Job status")
    message: str = Field(description="Status message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(description="Service status")
    timestamp: datetime = Field(description="Check timestamp")
    version: Optional[str] = Field("1.0.0", description="Service version")

class EntityData(BaseModel):
    """Schema for extracted entities"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = Field(description="Type of entity")
    text: str = Field(description="Entity text")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    start_pos: Optional[int] = Field(None, description="Start position in text")
    end_pos: Optional[int] = Field(None, description="End position in text")

class DocumentMetadata(BaseModel):
    """Schema for document metadata"""
    source: Optional[str] = Field(None, description="Document source")
    content_type: Optional[str] = Field(None, description="Content type")
    language: Optional[str] = Field("en", description="Document language")
    author: Optional[str] = Field(None, description="Document author")
    created_date: Optional[datetime] = Field(None, description="Document creation date")
    tags: Optional[List[str]] = Field(default_factory=list, description="Document tags")

class ProcessingResult(BaseModel):
    """Schema for ML processing results"""
    doc_type: str = Field(description="Classified document type")
    event_type: str = Field(description="Classified event type")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    entities: List[EntityData] = Field(default_factory=list, description="Extracted entities")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class JobStatus(BaseModel):
    """Schema for job status response"""
    job_id: str = Field(description="Job identifier")
    status: str = Field(description="Current status")
    doc_type: Optional[str] = Field(None, description="Document type")
    event_type: Optional[str] = Field(None, description="Event type")
    confidence: Optional[float] = Field(None, description="Classification confidence")
    entities: List[EntityData] = Field(default_factory=list, description="Extracted entities")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(description="Job creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

class JobList(BaseModel):
    """Schema for job listing response"""
    jobs: List[JobStatus] = Field(description="List of jobs")
    total: int = Field(description="Total number of jobs")
    skip: int = Field(description="Number of jobs skipped")
    limit: int = Field(description="Maximum jobs returned")

class StatsResponse(BaseModel):
    """Schema for statistics response"""
    total_documents: int = Field(description="Total documents processed")
    processed_documents: int = Field(description="Successfully processed documents")
    pending_documents: int = Field(description="Documents pending processing")
    failed_documents: int = Field(description="Failed documents")
    success_rate: float = Field(description="Success rate percentage")
    average_processing_time: Optional[float] = Field(None, description="Average processing time")

# Error response schemas
class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationError(BaseModel):
    """Schema for validation errors"""
    field: str = Field(description="Field with validation error")
    error: str = Field(description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value")

class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses"""
    error: str = Field("validation_error", description="Error type")
    message: str = Field(description="Error message")
    errors: List[ValidationError] = Field(description="List of validation errors")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
