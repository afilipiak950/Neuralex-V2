"""
Klassen: Document, Entity  (SQLAlchemy + UUID primary key)
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, Float, Integer, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class Document(Base):
    """
    Document model for storing processed documents
    """
    __tablename__ = "documents"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Source information
    gcs_uri = Column(String, nullable=True, index=True)
    payload = Column(JSON, nullable=True)
    
    # Processing status
    status = Column(String, nullable=False, default="pending", index=True)
    # Possible statuses: pending, processing, completed, failed
    
    # Classification results
    doc_type = Column(String, nullable=True, index=True)
    event_type = Column(String, nullable=True, index=True)
    confidence = Column(Float, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Metadata
    processing_time = Column(Float, nullable=True)  # in seconds
    model_version = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    entities = relationship("Entity", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, status={self.status}, doc_type={self.doc_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return {
            "id": self.id,
            "gcs_uri": self.gcs_uri,
            "payload": self.payload,
            "status": self.status,
            "doc_type": self.doc_type,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "entities": [entity.to_dict() for entity in self.entities] if self.entities else []
        }

class Entity(Base):
    """
    Entity model for storing extracted entities from documents
    """
    __tablename__ = "entities"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to document
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    
    # Entity information
    entity_type = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    
    # Position information
    start_pos = Column(Integer, nullable=True)
    end_pos = Column(Integer, nullable=True)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="entities")
    
    def __repr__(self):
        return f"<Entity(id={self.id}, type={self.entity_type}, text={self.text[:50]}...)>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "entity_type": self.entity_type,
            "text": self.text,
            "confidence": self.confidence,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ProcessingJob(Base):
    """
    Model for tracking background processing jobs
    """
    __tablename__ = "processing_jobs"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Job information
    job_type = Column(String, nullable=False, default="document_processing")
    status = Column(String, nullable=False, default="queued", index=True)
    # Possible statuses: queued, processing, completed, failed, cancelled
    
    # Job data
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    
    # Processing information
    worker_id = Column(String, nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    
    # Timing
    queued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Priority and scheduling
    priority = Column(Integer, nullable=False, default=0)  # Higher numbers = higher priority
    scheduled_for = Column(DateTime, nullable=True)  # For delayed execution
    
    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, type={self.job_type}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "worker_id": self.worker_id,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "error_message": self.error_message,
            "error_traceback": self.error_traceback,
            "queued_at": self.queued_at.isoformat() if self.queued_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "priority": self.priority,
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None
        }

class SystemStats(Base):
    """
    Model for storing system statistics and metrics
    """
    __tablename__ = "system_stats"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Metric information
    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)
    
    # Additional data
    tags = Column(JSON, nullable=True)  # For grouping and filtering
    
    # Timestamp
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SystemStats(metric={self.metric_name}, value={self.metric_value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        return {
            "id": self.id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "tags": self.tags,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None
        }

# Index definitions for performance
from sqlalchemy import Index

# Document indexes
Index('idx_documents_status_created', Document.status, Document.created_at)
Index('idx_documents_doc_type_confidence', Document.doc_type, Document.confidence)

# Entity indexes
Index('idx_entities_type_confidence', Entity.entity_type, Entity.confidence)
Index('idx_entities_document_type', Entity.document_id, Entity.entity_type)

# Job indexes
Index('idx_jobs_status_priority', ProcessingJob.status, ProcessingJob.priority.desc())
Index('idx_jobs_scheduled', ProcessingJob.scheduled_for)

# Stats indexes
Index('idx_stats_metric_time', SystemStats.metric_name, SystemStats.recorded_at.desc())
