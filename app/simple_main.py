"""
Simplified NeuraLex Platform - FastAPI Application
"""

import os
import logging
from fastapi import FastAPI, Request, Form, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import json
from datetime import datetime
from app.integrations.google_document_ai import document_ai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NeuraLex Platform",
    description="AI Document Processing Platform",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# In-memory storage for demo purposes
documents = {}
jobs = {}

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class IngestRequest(BaseModel):
    gcs_uri: Optional[str] = None
    payload: Optional[dict] = None

class IngestResponse(BaseModel):
    job_id: str
    status: str
    message: str

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("NeuraLex Platform starting up...")
    logger.info("Application initialized successfully")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main dashboard page"""
    return templates.TemplateResponse("modern_index.html", {
        "request": request,
        "title": "NeuraLex Platform"
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the dashboard page with document processing status"""
    # Calculate simple stats
    total_docs = len(documents)
    completed_docs = len([d for d in documents.values() if d.get("status") == "completed"])
    pending_docs = len([d for d in documents.values() if d.get("status") == "pending"])
    
    return templates.TemplateResponse("modern_dashboard.html", {
        "request": request,
        "title": "Dashboard - NeuraLex Platform",
        "total_documents": total_docs,
        "completed_documents": completed_docs,
        "pending_documents": pending_docs,
        "recent_documents": list(documents.values())[-10:]  # Last 10 documents
    })

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )

@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Document ingestion endpoint
    Accepts either GCS URI or direct payload and queues for ML processing
    """
    job_id = str(uuid.uuid4())
    
    # Validate input
    if not request.gcs_uri and not request.payload:
        return IngestResponse(
            job_id=job_id,
            status="error",
            message="Either gcs_uri or payload must be provided"
        )
    
    # Create document record
    doc_data = {
        "id": job_id,
        "gcs_uri": request.gcs_uri,
        "payload": request.payload,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    documents[job_id] = doc_data
    
    # Add background processing task
    background_tasks.add_task(process_document_background, job_id)
    
    logger.info(f"Document ingestion job created: {job_id}")
    
    return IngestResponse(
        job_id=job_id,
        status="accepted",
        message="Document queued for processing"
    )

@app.post("/ingest-form")
async def ingest_form(
    request: Request,
    background_tasks: BackgroundTasks,
    gcs_uri: Optional[str] = Form(None),
    text_content: Optional[str] = Form(None)
):
    """Handle form submission from the web interface"""
    job_id = str(uuid.uuid4())
    
    # Validate input
    if not gcs_uri and not text_content:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Please provide either a GCS URI or text content",
            "title": "NeuraLex Platform"
        })
    
    # Prepare payload
    payload = None
    if text_content:
        payload = {"content": text_content, "type": "text"}
    
    # Create document record
    doc_data = {
        "id": job_id,
        "gcs_uri": gcs_uri,
        "payload": payload,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    documents[job_id] = doc_data
    
    # Add background processing task
    background_tasks.add_task(process_document_background, job_id)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "success": f"Document submitted successfully! Job ID: {job_id}",
        "job_id": job_id,
        "title": "NeuraLex Platform"
    })

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get the status and results of a processing job"""
    if job_id not in documents:
        return {"error": "Job not found"}
    
    return documents[job_id]

@app.get("/jobs")
async def list_jobs(skip: int = 0, limit: int = 50):
    """List all processing jobs with pagination"""
    # Kombiniere lokale Dokumente mit Google Cloud OCR-Daten
    local_docs = list(documents.values())
    
    # Hole Google Cloud OCR-Dokumente falls konfiguriert
    try:
        gcp_docs = await document_ai_client.get_processed_documents(limit=limit)
        # Konvertiere GCP-Format in unser lokales Format
        for gcp_doc in gcp_docs:
            if gcp_doc["document_id"] not in documents:
                converted_doc = {
                    "id": gcp_doc["document_id"],
                    "status": gcp_doc["status"],
                    "created_at": gcp_doc["created_at"],
                    "updated_at": gcp_doc["created_at"],
                    "doc_type": gcp_doc.get("doc_type", "unknown"),
                    "confidence": gcp_doc.get("confidence", 0.0),
                    "entities": gcp_doc.get("entities", []),
                    "text": gcp_doc.get("text", ""),
                    "source": "google_cloud_ai"
                }
                local_docs.append(converted_doc)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der GCP-Dokumente: {e}")
    
    # Sortiere nach Erstellungsdatum
    all_docs = sorted(local_docs, key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {
        "jobs": all_docs[skip:skip + limit],
        "total": len(all_docs),
        "skip": skip,
        "limit": limit
    }

async def process_document_background(job_id: str):
    """Background task to process documents"""
    import asyncio
    import random
    
    try:
        # Simulate processing delay
        await asyncio.sleep(2)
        
        # Update status to processing
        if job_id in documents:
            documents[job_id]["status"] = "processing"
            documents[job_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Simulate ML processing delay
        await asyncio.sleep(3)
        
        # Simulate successful processing
        if job_id in documents:
            documents[job_id]["status"] = "completed"
            documents[job_id]["doc_type"] = "invoice"
            documents[job_id]["confidence"] = round(random.uniform(0.8, 0.99), 2)
            documents[job_id]["entities"] = [
                {"type": "amount", "text": "$1,234.56", "confidence": 0.95},
                {"type": "date", "text": "2024-01-15", "confidence": 0.92},
                {"type": "vendor", "text": "Acme Corp", "confidence": 0.89}
            ]
            documents[job_id]["updated_at"] = datetime.utcnow().isoformat()
            
        logger.info(f"Document processing completed: {job_id}")
        
    except Exception as e:
        # Handle processing errors
        if job_id in documents:
            documents[job_id]["status"] = "failed"
            documents[job_id]["error_message"] = str(e)
            documents[job_id]["updated_at"] = datetime.utcnow().isoformat()
        
        logger.error(f"Document processing failed: {job_id}, error: {e}")

@app.get("/api/gcp/documents")
async def get_gcp_documents(limit: int = 10, search: str = None):
    """Hole Dokumente direkt aus Google Cloud Document AI"""
    try:
        if search:
            gcp_docs = await document_ai_client.search_documents(search, limit)
        else:
            gcp_docs = await document_ai_client.get_processed_documents(limit)
            
        return {
            "documents": gcp_docs,
            "total": len(gcp_docs),
            "source": "google_cloud_document_ai",
            "configured": document_ai_client.is_configured
        }
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der GCP-Dokumente: {e}")
        return {
            "documents": [],
            "total": 0,
            "error": str(e),
            "configured": document_ai_client.is_configured
        }

@app.get("/api/gcp/document/{document_id}")
async def get_gcp_document(document_id: str):
    """Hole ein spezifisches Dokument aus Google Cloud"""
    try:
        doc = await document_ai_client.query_document_by_id(document_id)
        if doc:
            return doc
        else:
            return {"error": "Document not found"}
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Dokuments {document_id}: {e}")
        return {"error": str(e)}

@app.get("/api/search")
async def search_all_documents(q: str, limit: int = 20):
    """Durchsuche alle Dokumente (lokal + Google Cloud)"""
    results = []
    
    # Lokale Dokumente durchsuchen
    for doc in documents.values():
        text_content = doc.get("payload", {}).get("content", "") if doc.get("payload") else ""
        if q.lower() in text_content.lower() or q.lower() in doc.get("id", "").lower():
            results.append({**doc, "source": "local"})
    
    # Google Cloud Dokumente durchsuchen
    try:
        gcp_results = await document_ai_client.search_documents(q, limit//2)
        for gcp_doc in gcp_results:
            results.append({
                "id": gcp_doc["document_id"],
                "text": gcp_doc.get("text", ""),
                "entities": gcp_doc.get("entities", []),
                "doc_type": gcp_doc.get("doc_type", "unknown"),
                "confidence": gcp_doc.get("confidence", 0.0),
                "created_at": gcp_doc.get("created_at", ""),
                "source": "google_cloud_ai"
            })
    except Exception as e:
        logger.error(f"Fehler bei der GCP-Suche: {e}")
    
    # Limitiere und sortiere Ergebnisse
    results = sorted(results, key=lambda x: x.get("confidence", 0.0), reverse=True)[:limit]
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

@app.get("/api/config/status")
async def get_configuration_status():
    """Zeige den Konfigurationsstatus der Integrationen"""
    return {
        "google_cloud_ai": {
            "configured": document_ai_client.is_configured,
            "project_id": document_ai_client.project_id,
            "location": document_ai_client.location,
            "processor_id": document_ai_client.processor_id
        },
        "database": {
            "type": "in_memory",
            "documents_count": len(documents)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)