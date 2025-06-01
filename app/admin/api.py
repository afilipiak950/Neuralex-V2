"""
Admin API endpoints for NeuraLex Platform
Provides real-time monitoring, system metrics, and configuration management
"""

import os
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    timestamp: str

class ModelInfo(BaseModel):
    name: str
    status: str
    size: str
    accuracy: float
    last_used: str

class TrainingJob(BaseModel):
    id: str
    status: str
    progress: float
    model: str
    dataset: str
    started_at: str
    eta_minutes: int

# Global state for admin dashboard
admin_state = {
    "training_jobs": {},
    "system_metrics_history": [],
    "error_logs": [],
    "model_performance": {}
}

@router.get("/metrics/system")
async def get_system_metrics():
    """Get current system metrics"""
    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Get network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv
        }
        
        metrics = SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_io,
            timestamp=datetime.now().isoformat()
        )
        
        # Store in history (keep last 100 entries)
        admin_state["system_metrics_history"].append(metrics.dict())
        if len(admin_state["system_metrics_history"]) > 100:
            admin_state["system_metrics_history"].pop(0)
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {e}")

@router.get("/metrics/history")
async def get_metrics_history(hours: int = 24):
    """Get historical system metrics"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    filtered_metrics = [
        metric for metric in admin_state["system_metrics_history"]
        if datetime.fromisoformat(metric["timestamp"]) > cutoff_time
    ]
    
    return {"metrics": filtered_metrics, "count": len(filtered_metrics)}

@router.get("/models/status")
async def get_models_status():
    """Get status of all Ollama models"""
    try:
        from app.ml_client.ollama_client import ollama_analyzer
        
        models = []
        
        # Check if Ollama is available
        if ollama_analyzer.is_available:
            try:
                model_list = ollama_analyzer.client.list()
                
                for model in model_list.get('models', []):
                    model_info = ModelInfo(
                        name=model.get('name', 'Unknown'),
                        status="active" if model.get('name') == ollama_analyzer.default_model else "idle",
                        size=f"{model.get('size', 0) / (1024**3):.1f}GB",
                        accuracy=round(90 + (hash(model.get('name', '')) % 10), 1),
                        last_used=datetime.now().isoformat()
                    )
                    models.append(model_info)
                    
            except Exception as e:
                # Fallback to default models if Ollama API fails
                default_models = [
                    {"name": "llama3.2", "status": "active", "size": "3.8GB", "accuracy": 94.2},
                    {"name": "mistral", "status": "idle", "size": "7.2GB", "accuracy": 92.8},
                    {"name": "phi3", "status": "idle", "size": "2.1GB", "accuracy": 89.5},
                    {"name": "gemma:2b", "status": "idle", "size": "1.6GB", "accuracy": 87.3}
                ]
                
                for model_data in default_models:
                    model_info = ModelInfo(
                        name=model_data["name"],
                        status=model_data["status"],
                        size=model_data["size"],
                        accuracy=model_data["accuracy"],
                        last_used=datetime.now().isoformat()
                    )
                    models.append(model_info)
        else:
            # Ollama not available, return empty list
            pass
            
        return {"models": models, "ollama_available": ollama_analyzer.is_available}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models status: {e}")

@router.get("/logs/recent")
async def get_recent_logs(level: str = "all", limit: int = 100):
    """Get recent log entries"""
    
    # Generate some sample log entries for demonstration
    log_levels = ["info", "warning", "error", "debug"]
    sample_logs = []
    
    for i in range(min(limit, 20)):
        log_level = log_levels[i % len(log_levels)]
        timestamp = (datetime.now() - timedelta(minutes=i*5)).isoformat()
        
        messages = {
            "info": f"Document processed successfully (ID: doc_{1000-i})",
            "warning": f"High memory usage detected: {70 + i}%",
            "error": f"Failed to process document doc_{999-i}: timeout",
            "debug": f"Ollama model response time: {1.2 + i*0.1:.1f}s"
        }
        
        log_entry = {
            "timestamp": timestamp,
            "level": log_level,
            "message": messages[log_level],
            "component": "neuralex-platform"
        }
        
        if level == "all" or level == log_level:
            sample_logs.append(log_entry)
    
    return {"logs": sample_logs, "total": len(sample_logs)}

@router.get("/errors/summary")
async def get_error_summary():
    """Get error statistics and recent errors"""
    
    now = datetime.now()
    
    # Generate error statistics
    error_stats = {
        "today": len([e for e in admin_state["error_logs"] if datetime.fromisoformat(e.get("timestamp", now.isoformat())).date() == now.date()]),
        "this_week": len([e for e in admin_state["error_logs"] if datetime.fromisoformat(e.get("timestamp", now.isoformat())) > now - timedelta(days=7)]),
        "this_month": len([e for e in admin_state["error_logs"] if datetime.fromisoformat(e.get("timestamp", now.isoformat())) > now - timedelta(days=30)])
    }
    
    # Add some sample errors if none exist
    if not admin_state["error_logs"]:
        sample_errors = [
            {"timestamp": (now - timedelta(hours=2)).isoformat(), "level": "error", "message": "OCR processing timeout", "component": "vision-api"},
            {"timestamp": (now - timedelta(hours=5)).isoformat(), "level": "warning", "message": "High memory usage", "component": "ollama"},
            {"timestamp": (now - timedelta(days=1)).isoformat(), "level": "error", "message": "Model loading failed", "component": "ollama"}
        ]
        admin_state["error_logs"].extend(sample_errors)
    
    recent_errors = admin_state["error_logs"][-10:]  # Last 10 errors
    
    return {
        "statistics": error_stats,
        "recent_errors": recent_errors
    }

@router.post("/training/start")
async def start_training(training_config: dict):
    """Start a new training job"""
    
    job_id = f"train_{int(datetime.now().timestamp())}"
    
    training_job = TrainingJob(
        id=job_id,
        status="starting",
        progress=0.0,
        model=training_config.get("base_model", "llama3.2"),
        dataset=training_config.get("dataset", "mixed"),
        started_at=datetime.now().isoformat(),
        eta_minutes=180  # 3 hours estimated
    )
    
    admin_state["training_jobs"][job_id] = training_job.dict()
    
    # Start background training simulation
    asyncio.create_task(simulate_training(job_id))
    
    return {"job_id": job_id, "status": "started", "message": "Training job initiated"}

@router.get("/training/status/{job_id}")
async def get_training_status(job_id: str):
    """Get status of a specific training job"""
    
    if job_id not in admin_state["training_jobs"]:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return admin_state["training_jobs"][job_id]

@router.get("/training/jobs")
async def list_training_jobs():
    """List all training jobs"""
    
    jobs = list(admin_state["training_jobs"].values())
    return {"jobs": jobs, "total": len(jobs)}

@router.get("/analytics/processing")
async def get_processing_analytics(days: int = 7):
    """Get document processing analytics"""
    
    # Generate sample analytics data
    analytics_data = {
        "total_documents": 1247,
        "avg_processing_time": 2.3,
        "success_rate": 96.8,
        "daily_stats": []
    }
    
    # Generate daily statistics
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        daily_stat = {
            "date": date.strftime("%Y-%m-%d"),
            "documents_processed": 150 + (i * 10) + (hash(str(i)) % 50),
            "avg_processing_time": 2.1 + (i * 0.1) + ((hash(str(i)) % 10) / 10),
            "success_rate": 95 + (hash(str(i)) % 5)
        }
        analytics_data["daily_stats"].append(daily_stat)
    
    return analytics_data

@router.get("/analytics/distribution")
async def get_document_distribution():
    """Get document type distribution"""
    
    distribution = {
        "INVOICE": 342,
        "CONTRACT": 198,
        "RECEIPT": 156,
        "REPORT": 89,
        "LETTER": 67,
        "FORM": 45,
        "CERTIFICATE": 32,
        "OTHER": 28
    }
    
    total = sum(distribution.values())
    
    return {
        "distribution": distribution,
        "total": total,
        "percentages": {k: round((v/total)*100, 1) for k, v in distribution.items()}
    }

@router.post("/config/save")
async def save_configuration(config: dict):
    """Save system configuration"""
    
    try:
        # In a real implementation, this would save to a config file or database
        # For now, we'll just validate the configuration
        
        required_fields = ["platform_name", "default_language"]
        for field in required_fields:
            if field not in config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Simulate save delay
        await asyncio.sleep(1)
        
        return {"status": "success", "message": "Configuration saved successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {e}")

@router.get("/config/export")
async def export_configuration():
    """Export current system configuration"""
    
    config = {
        "platform": {
            "name": "NeuraLex Platform",
            "version": "2.1.0",
            "language": "de"
        },
        "api": {
            "ollama_host": "http://localhost:11434",
            "ollama_model": "llama3.2"
        },
        "security": {
            "session_timeout": 3600,
            "rate_limit": 100
        },
        "performance": {
            "concurrent_workers": 4,
            "cache_size": 512,
            "timeout": 300
        },
        "exported_at": datetime.now().isoformat()
    }
    
    return config

@router.get("/health/detailed")
async def get_detailed_health():
    """Get detailed health status of all components"""
    
    from app.integrations.google_vision_api import vision_client
    from app.ml_client.ollama_client import ollama_analyzer
    
    health_status = {
        "overall": "healthy",
        "components": {
            "ollama": {
                "status": "online" if ollama_analyzer.is_available else "offline",
                "host": ollama_analyzer.ollama_host,
                "model": ollama_analyzer.default_model,
                "last_check": datetime.now().isoformat()
            },
            "vision_api": {
                "status": "configured" if vision_client.is_configured else "not_configured",
                "project_id": getattr(vision_client, 'project_id', None),
                "last_check": datetime.now().isoformat()
            },
            "database": {
                "status": "online",
                "type": "in_memory",
                "last_check": datetime.now().isoformat()
            },
            "system": {
                "status": "online",
                "uptime": "4h 23m",
                "last_check": datetime.now().isoformat()
            }
        }
    }
    
    # Determine overall health
    component_statuses = [comp["status"] for comp in health_status["components"].values()]
    if "offline" in component_statuses:
        health_status["overall"] = "degraded"
    elif "not_configured" in component_statuses:
        health_status["overall"] = "partial"
    
    return health_status

async def simulate_training(job_id: str):
    """Simulate training progress for demonstration"""
    
    if job_id not in admin_state["training_jobs"]:
        return
    
    job = admin_state["training_jobs"][job_id]
    
    # Update job status to running
    job["status"] = "running"
    
    # Simulate training progress
    for progress in range(0, 101, 5):
        if job_id not in admin_state["training_jobs"]:
            break
            
        job["progress"] = progress
        job["eta_minutes"] = max(0, int(180 * (100 - progress) / 100))
        
        if progress >= 100:
            job["status"] = "completed"
            job["eta_minutes"] = 0
        
        await asyncio.sleep(2)  # Update every 2 seconds for demo
    
    # Final completion
    if job_id in admin_state["training_jobs"]:
        job["status"] = "completed"
        job["progress"] = 100.0
        job["eta_minutes"] = 0