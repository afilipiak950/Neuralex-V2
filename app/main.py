"""
FastAPI-App mit:
  – /health          GET   -> {"status": "ok"}
  – /ingest          POST  -> nimmt {gcs_uri:str} oder {payload:dict}
  – ruft async gcp_fetcher.fetch()
  – pushed Job in Redis-Queue (key: 'doc_jobs')
  – background-worker konsumiert, ruft ml_client.predict(), speichert Ergebnis in DB

TODO: Implement background-worker mit aioredis Subscriber  
TODO: Add Alembic migrations (optional)  
TODO: Add retry-logic in ml_client.predict()  
TODO: Add /docs (Swagger) with JWT auth stubs  
TODO: Map JSON-Schemas → Pydantic-Models
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db, engine
from app.db.models import Document, Entity, Base
from app.ingestion.gcp_fetcher import fetch_from_gcs
from app.ml_client.predict import predict_document
from app.schemas.data_types import IngestRequest, IngestResponse, HealthResponse
from app.utils.mapping import map_label_to_id, map_id_to_label

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="NeuraLex Platform",
    description="AI-powered document processing and classification platform",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and Redis connections on startup"""
    global redis_client
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        
        # Initialize Redis connection
        redis_client = await aioredis.from_url(REDIS_URL)
        logger.info("Redis connection established")
        
        # Start background worker
        asyncio.create_task(background_worker())
        logger.info("Background worker started")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the dashboard page with document processing status"""
    try:
        async with get_db() as db:
            # Get recent documents
            result = await db.execute(
                select(Document).order_by(Document.created_at.desc()).limit(10)
            )
            documents = result.scalars().all()
            
            # Get processing statistics
            total_docs = await db.execute(select(Document).count())
            total_count = total_docs.scalar()
            
            processed_docs = await db.execute(
                select(Document).where(Document.status == "completed").count()
            )
            processed_count = processed_docs.scalar()
            
            stats = {
                "total_documents": total_count,
                "processed_documents": processed_count,
                "pending_documents": total_count - processed_count,
                "success_rate": round((processed_count / total_count * 100) if total_count > 0 else 0, 2)
            }
            
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "documents": documents,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "documents": [],
            "stats": {"total_documents": 0, "processed_documents": 0, "pending_documents": 0, "success_rate": 0},
            "error": str(e)
        })

# API Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        async with get_db() as db:
            await db.execute(select(1))
        
        # Test Redis connection
        if redis_client:
            await redis_client.ping()
        
        return HealthResponse(status="ok", timestamp=datetime.utcnow())
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")

@app.post("/ingest", response_model=IngestResponse, status_code=202)
async def ingest_document(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Document ingestion endpoint
    Accepts either GCS URI or direct payload and queues for ML processing
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Create document record
        async with get_db() as db:
            document = Document(
                id=job_id,
                gcs_uri=request.gcs_uri,
                payload=request.payload,
                status="pending",
                created_at=datetime.utcnow()
            )
            db.add(document)
            await db.commit()
        
        # Queue job for background processing
        job_data = {
            "job_id": job_id,
            "gcs_uri": request.gcs_uri,
            "payload": request.payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await redis_client.lpush("doc_jobs", json.dumps(job_data))
        logger.info(f"Queued job {job_id} for processing")
        
        return IngestResponse(
            job_id=job_id,
            status="queued",
            message="Document queued for processing"
        )
        
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get the status and results of a processing job"""
    try:
        async with get_db() as db:
            result = await db.execute(select(Document).where(Document.id == job_id))
            document = result.scalar_one_or_none()
            
            if not document:
                raise HTTPException(status_code=404, detail="Job not found")
            
            # Get associated entities
            entities_result = await db.execute(
                select(Entity).where(Entity.document_id == job_id)
            )
            entities = entities_result.scalars().all()
            
            return {
                "job_id": job_id,
                "status": document.status,
                "doc_type": document.doc_type,
                "event_type": document.event_type,
                "confidence": document.confidence,
                "entities": [
                    {
                        "id": entity.id,
                        "entity_type": entity.entity_type,
                        "text": entity.text,
                        "confidence": entity.confidence,
                        "start_pos": entity.start_pos,
                        "end_pos": entity.end_pos
                    }
                    for entity in entities
                ],
                "error_message": document.error_message,
                "created_at": document.created_at,
                "updated_at": document.updated_at
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {e}")

@app.get("/jobs")
async def list_jobs(skip: int = 0, limit: int = 50):
    """List all processing jobs with pagination"""
    try:
        async with get_db() as db:
            result = await db.execute(
                select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit)
            )
            documents = result.scalars().all()
            
            return {
                "jobs": [
                    {
                        "job_id": doc.id,
                        "status": doc.status,
                        "doc_type": doc.doc_type,
                        "event_type": doc.event_type,
                        "confidence": doc.confidence,
                        "created_at": doc.created_at,
                        "updated_at": doc.updated_at
                    }
                    for doc in documents
                ],
                "total": len(documents),
                "skip": skip,
                "limit": limit
            }
            
    except Exception as e:
        logger.error(f"List jobs error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {e}")

async def background_worker():
    """
    Background worker that processes jobs from Redis queue
    TODO: Implement background-worker mit aioredis Subscriber
    """
    logger.info("Background worker started")
    
    while True:
        try:
            # Pop job from queue (blocking with timeout)
            job_data = await redis_client.brpop("doc_jobs", timeout=5)
            
            if job_data:
                queue_name, job_json = job_data
                job = json.loads(job_json)
                
                await process_job(job)
                
        except Exception as e:
            logger.error(f"Background worker error: {e}")
            await asyncio.sleep(5)  # Wait before retrying

async def process_job(job: Dict[str, Any]):
    """Process a single job from the queue"""
    job_id = job["job_id"]
    logger.info(f"Processing job {job_id}")
    
    try:
        async with get_db() as db:
            # Update status to processing
            result = await db.execute(select(Document).where(Document.id == job_id))
            document = result.scalar_one()
            document.status = "processing"
            document.updated_at = datetime.utcnow()
            await db.commit()
        
        # Fetch document content
        if job.get("gcs_uri"):
            content = await fetch_from_gcs(job["gcs_uri"])
        else:
            content = job.get("payload", {})
        
        # Get ML prediction
        prediction = await predict_document(content)
        
        # Store results in database
        async with get_db() as db:
            # Update document with prediction results
            result = await db.execute(select(Document).where(Document.id == job_id))
            document = result.scalar_one()
            
            document.status = "completed"
            document.doc_type = prediction.get("doc_type")
            document.event_type = prediction.get("event_type")
            document.confidence = prediction.get("confidence", 0.0)
            document.updated_at = datetime.utcnow()
            
            # Create entity records
            entities_data = prediction.get("entities", [])
            for entity_data in entities_data:
                entity = Entity(
                    document_id=job_id,
                    entity_type=entity_data.get("type"),
                    text=entity_data.get("text"),
                    confidence=entity_data.get("confidence", 0.0),
                    start_pos=entity_data.get("start_pos"),
                    end_pos=entity_data.get("end_pos")
                )
                db.add(entity)
            
            await db.commit()
            
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        
        # Update status to failed
        try:
            async with get_db() as db:
                result = await db.execute(select(Document).where(Document.id == job_id))
                document = result.scalar_one()
                document.status = "failed"
                document.error_message = str(e)
                document.updated_at = datetime.utcnow()
                await db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update job {job_id} status: {db_error}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
