"""
Simplified NeuraLex Platform - FastAPI Application
"""

import os
import logging
from fastapi import FastAPI, Request, Form, BackgroundTasks, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import json
from datetime import datetime
from app.integrations.google_vision_api import vision_client
from app.ml_client.ollama_client import ollama_analyzer
from app.admin.api import router as admin_router

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

# Include admin API routes
app.include_router(admin_router)

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

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Serve the comprehensive admin dashboard"""
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "title": "NeuraLex Admin Dashboard"
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
        gcp_docs = await vision_client.search_processed_documents("", limit=limit)
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
                    "source": "google_vision_api"
                }
                local_docs.append(converted_doc)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Vision API Dokumente: {e}")
    
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

@app.post("/api/ollama/analyze")
async def analyze_document_with_ollama(request: Request):
    """Analysiert OCR-JSON-Daten mit Ollama und extrahiert strukturierte Informationen"""
    try:
        # Lese JSON-Daten aus Request
        ocr_data = await request.json()
        
        # Analysiere mit Ollama
        result = await ollama_analyzer.analyze_document(ocr_data)
        
        if "error" in result:
            return {"error": result["error"], "ollama_available": ollama_analyzer.is_available}
        
        # Speichere Ergebnis lokal
        job_id = result["document_id"]
        documents[job_id] = {
            "id": job_id,
            "status": result["status"],
            "created_at": result["processed_at"],
            "updated_at": result["processed_at"],
            "source": "ollama_analysis",
            "doc_type": result["doc_type"],
            "event_type": result["event_type"],
            "confidence": result["confidence"],
            "extracted_data": result["extracted_data"],
            "original_text": result.get("original_text", ""),
            "processor": result["processor"],
            "model": result["model"]
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Fehler bei Ollama-Analyse: {e}")
        return {"error": str(e), "ollama_available": ollama_analyzer.is_available}

@app.post("/api/process/complete")
async def complete_document_processing(file: UploadFile = File(...)):
    """Vollständige Dokumentverarbeitung: OCR + Ollama-Analyse"""
    try:
        # Schritt 1: OCR mit Vision API
        image_data = await file.read()
        ocr_result = await vision_client.perform_ocr(image_data, file.content_type or "image/png")
        
        if "error" in ocr_result:
            return {"error": f"OCR fehlgeschlagen: {ocr_result['error']}", "stage": "ocr"}
        
        # Schritt 2: Ollama-Analyse der OCR-Daten
        analysis_result = await ollama_analyzer.analyze_document(ocr_result)
        
        if "error" in analysis_result:
            return {"error": f"Analyse fehlgeschlagen: {analysis_result['error']}", "stage": "analysis"}
        
        # Kombiniere OCR + Analyse Ergebnisse
        final_result = {
            "document_id": analysis_result["document_id"],
            "status": "completed",
            "filename": file.filename,
            "processing_stages": {
                "ocr": {
                    "completed": True,
                    "source": "google_vision_api",
                    "raw_text": ocr_result.get("text", "")
                },
                "analysis": {
                    "completed": True,
                    "source": "ollama",
                    "model": analysis_result["model"]
                }
            },
            "doc_type": analysis_result["doc_type"],
            "event_type": analysis_result["event_type"],
            "confidence": analysis_result["confidence"],
            "extracted_data": analysis_result["extracted_data"],
            "created_at": analysis_result["processed_at"],
            "updated_at": analysis_result["processed_at"]
        }
        
        # Speichere vollständiges Ergebnis
        job_id = final_result["document_id"]
        documents[job_id] = final_result
        
        return final_result
        
    except Exception as e:
        logger.error(f"Fehler bei vollständiger Dokumentverarbeitung: {e}")
        return {"error": str(e), "stage": "unknown"}

@app.post("/api/vision/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    """Führt OCR auf einem hochgeladenen Bild durch"""
    try:
        # Lese Bilddaten
        image_data = await file.read()
        
        # Führe OCR über Vision API durch
        result = await vision_client.perform_ocr(image_data, file.content_type or "image/png")
        
        if "error" in result:
            return {"error": result["error"], "configured": vision_client.is_configured}
        
        # Speichere Ergebnis lokal
        job_id = result["document_id"]
        documents[job_id] = {
            "id": job_id,
            "status": "completed",
            "created_at": result["created_at"],
            "updated_at": result["created_at"],
            "source": "google_vision_api",
            "filename": file.filename,
            "text": result["text"],
            "entities": result["entities"],
            "confidence": result["confidence"]
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Fehler bei OCR-Verarbeitung: {e}")
        return {"error": str(e), "configured": vision_client.is_configured}

@app.post("/api/vision/ocr-url")
async def perform_ocr_from_url(image_url: str):
    """Führt OCR auf einem Bild von einer URL durch"""
    try:
        result = await vision_client.process_document_from_url(image_url)
        
        if "error" in result:
            return {"error": result["error"], "configured": vision_client.is_configured}
        
        # Speichere Ergebnis lokal
        job_id = result["document_id"]
        documents[job_id] = {
            "id": job_id,
            "status": "completed",
            "created_at": result["created_at"],
            "updated_at": result["created_at"],
            "source": "google_vision_api",
            "image_url": image_url,
            "text": result["text"],
            "entities": result["entities"],
            "confidence": result["confidence"]
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Fehler bei OCR von URL: {e}")
        return {"error": str(e), "configured": vision_client.is_configured}

@app.get("/api/search")
async def search_all_documents(q: str, limit: int = 20):
    """Durchsuche alle Dokumente (lokal + Google Cloud)"""
    results = []
    
    # Lokale Dokumente durchsuchen
    for doc in documents.values():
        text_content = doc.get("payload", {}).get("content", "") if doc.get("payload") else ""
        if q.lower() in text_content.lower() or q.lower() in doc.get("id", "").lower():
            results.append({**doc, "source": "local"})
    
    # Vision API Dokumente durchsuchen
    try:
        gcp_results = await vision_client.search_processed_documents(q, limit//2)
        for gcp_doc in gcp_results:
            results.append({
                "id": gcp_doc["document_id"],
                "text": gcp_doc.get("text", ""),
                "entities": gcp_doc.get("entities", []),
                "doc_type": gcp_doc.get("doc_type", "unknown"),
                "confidence": gcp_doc.get("confidence", 0.0),
                "created_at": gcp_doc.get("created_at", ""),
                "source": "google_vision_api"
            })
    except Exception as e:
        logger.error(f"Fehler bei der Vision API Suche: {e}")
    
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
        "google_vision_api": {
            "configured": vision_client.is_configured,
            "project_id": vision_client.project_id if hasattr(vision_client, 'project_id') else None
        },
        "ollama": {
            "available": ollama_analyzer.is_available,
            "host": ollama_analyzer.ollama_host,
            "model": ollama_analyzer.default_model
        },
        "database": {
            "type": "in_memory",
            "documents_count": len(documents)
        },
        "supported_doc_types": [
            "INVOICE", "CONTRACT", "RECEIPT", "LETTER", 
            "FORM", "CERTIFICATE", "REPORT", "OTHER"
        ],
        "supported_event_types": [
            "PAYMENT_DUE", "CONTRACT_SIGNED", "PAYMENT_CONFIRMED",
            "DOCUMENT_PROCESSED", "ANALYSIS_COMPLETED"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)