"""
Background worker implementation for processing document jobs
TODO: Implement background-worker mit aioredis Subscriber
"""

import os
import json
import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

import aioredis
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Document, Entity, ProcessingJob
from app.ingestion.gcp_fetcher import fetch_from_gcs
from app.ml_client.predict import predict_document
from app.utils.mapping import map_label_to_id

logger = logging.getLogger(__name__)

class BackgroundWorker:
    """
    Background worker for processing document jobs from Redis queue
    """
    
    def __init__(self, worker_id: Optional[str] = None):
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.redis_client = None
        self.running = False
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.queue_name = "doc_jobs"
        self.batch_size = int(os.getenv("WORKER_BATCH_SIZE", "1"))
        self.poll_interval = float(os.getenv("WORKER_POLL_INTERVAL", "1.0"))
        self.max_retries = int(os.getenv("WORKER_MAX_RETRIES", "3"))
        
        # Graceful shutdown handling
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the background worker"""
        logger.info(f"Starting background worker {self.worker_id}")
        
        try:
            # Initialize Redis connection
            self.redis_client = await aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info(f"Connected to Redis: {self.redis_url}")
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            self.running = True
            
            # Start main processing loop
            await self._process_loop()
            
        except Exception as e:
            logger.error(f"Failed to start worker {self.worker_id}: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def stop(self):
        """Stop the background worker gracefully"""
        logger.info(f"Stopping background worker {self.worker_id}")
        self.running = False
        self._shutdown_event.set()
    
    async def cleanup(self):
        """Clean up resources"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info(f"Closed Redis connection for worker {self.worker_id}")
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _process_loop(self):
        """Main processing loop"""
        logger.info(f"Worker {self.worker_id} entering processing loop")
        
        while self.running and not self._shutdown_event.is_set():
            try:
                # Check for jobs with timeout
                await asyncio.wait_for(
                    self._process_batch(),
                    timeout=self.poll_interval
                )
                
            except asyncio.TimeoutError:
                # No jobs available, continue polling
                pass
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info(f"Worker {self.worker_id} exiting processing loop")
    
    async def _process_batch(self):
        """Process a batch of jobs"""
        jobs_processed = 0
        
        while jobs_processed < self.batch_size and self.running:
            # Pop job from queue (blocking with timeout)
            job_data = await self.redis_client.brpop(
                self.queue_name, 
                timeout=int(self.poll_interval)
            )
            
            if not job_data:
                break  # No jobs available
            
            queue_name, job_json = job_data
            
            try:
                job = json.loads(job_json)
                await self._process_job(job)
                jobs_processed += 1
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid job JSON: {e}")
            except Exception as e:
                logger.error(f"Failed to process job: {e}")
                # Optionally, push job to dead letter queue
                await self._handle_failed_job(job_json, str(e))
    
    async def _process_job(self, job: Dict[str, Any]):
        """Process a single job"""
        job_id = job.get("job_id")
        if not job_id:
            logger.error("Job missing job_id")
            return
        
        start_time = datetime.utcnow()
        logger.info(f"Worker {self.worker_id} processing job {job_id}")
        
        try:
            # Update job status to processing
            async with get_db() as db:
                result = await db.execute(select(Document).where(Document.id == job_id))
                document = result.scalar_one_or_none()
                
                if not document:
                    logger.error(f"Document not found for job {job_id}")
                    return
                
                document.status = "processing"
                document.updated_at = datetime.utcnow()
                await db.commit()
            
            # Fetch document content
            content = await self._fetch_content(job)
            
            # Get ML prediction
            prediction = await predict_document(content)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Store results in database
            await self._store_results(job_id, prediction, processing_time)
            
            logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            await self._handle_job_failure(job_id, str(e))
    
    async def _fetch_content(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch document content from GCS or use direct payload"""
        gcs_uri = job.get("gcs_uri")
        payload = job.get("payload")
        
        if gcs_uri:
            logger.info(f"Fetching content from GCS: {gcs_uri}")
            return await fetch_from_gcs(gcs_uri)
        elif payload:
            logger.info("Using direct payload")
            return payload
        else:
            raise ValueError("No content source provided (gcs_uri or payload)")
    
    async def _store_results(self, job_id: str, prediction: Dict[str, Any], processing_time: float):
        """Store prediction results in database"""
        async with get_db() as db:
            # Update document with prediction results
            result = await db.execute(select(Document).where(Document.id == job_id))
            document = result.scalar_one()
            
            document.status = "completed"
            document.doc_type = prediction.get("doc_type")
            document.event_type = prediction.get("event_type")
            document.confidence = prediction.get("confidence", 0.0)
            document.processing_time = processing_time
            document.model_version = prediction.get("model_version", "1.0")
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
                    end_pos=entity_data.get("end_pos"),
                    metadata=entity_data.get("metadata")
                )
                db.add(entity)
            
            await db.commit()
    
    async def _handle_job_failure(self, job_id: str, error_message: str):
        """Handle job failure by updating status"""
        try:
            async with get_db() as db:
                result = await db.execute(select(Document).where(Document.id == job_id))
                document = result.scalar_one_or_none()
                
                if document:
                    document.status = "failed"
                    document.error_message = error_message
                    document.updated_at = datetime.utcnow()
                    await db.commit()
                    
        except Exception as e:
            logger.error(f"Failed to update job {job_id} failure status: {e}")
    
    async def _handle_failed_job(self, job_json: str, error: str):
        """Handle malformed or failed jobs"""
        # Push to dead letter queue
        dead_letter_queue = f"{self.queue_name}:failed"
        
        failed_job = {
            "original_job": job_json,
            "error": error,
            "worker_id": self.worker_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.lpush(dead_letter_queue, json.dumps(failed_job))
        logger.info(f"Moved failed job to dead letter queue: {dead_letter_queue}")
    
    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        try:
            # Get queue length
            queue_length = await self.redis_client.llen(self.queue_name)
            
            # Get dead letter queue length
            dead_letter_queue = f"{self.queue_name}:failed"
            failed_jobs = await self.redis_client.llen(dead_letter_queue)
            
            return {
                "worker_id": self.worker_id,
                "status": "running" if self.running else "stopped",
                "queue_length": queue_length,
                "failed_jobs": failed_jobs,
                "redis_connected": bool(self.redis_client),
                "poll_interval": self.poll_interval,
                "batch_size": self.batch_size,
                "max_retries": self.max_retries
            }
            
        except Exception as e:
            logger.error(f"Failed to get worker stats: {e}")
            return {
                "worker_id": self.worker_id,
                "status": "error",
                "error": str(e)
            }

# Global worker instance
_worker_instance = None

async def start_background_worker() -> BackgroundWorker:
    """Start the global background worker"""
    global _worker_instance
    
    if _worker_instance and _worker_instance.running:
        logger.warning("Background worker already running")
        return _worker_instance
    
    _worker_instance = BackgroundWorker()
    
    # Start worker in background task
    asyncio.create_task(_worker_instance.start())
    
    # Wait a bit to ensure worker is started
    await asyncio.sleep(1)
    
    return _worker_instance

async def stop_background_worker():
    """Stop the global background worker"""
    global _worker_instance
    
    if _worker_instance:
        await _worker_instance.stop()
        _worker_instance = None

async def get_worker_stats() -> Dict[str, Any]:
    """Get statistics for the global worker"""
    global _worker_instance
    
    if _worker_instance:
        return await _worker_instance.get_worker_stats()
    else:
        return {
            "status": "not_running",
            "error": "No worker instance found"
        }

# Command-line interface for running worker standalone
async def main():
    """Main function for running worker as standalone process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    worker = BackgroundWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        sys.exit(1)
    finally:
        await worker.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
