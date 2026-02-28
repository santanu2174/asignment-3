from fastapi import FastAPI, BackgroundTasks, UploadFile, File, HTTPException
import uuid
import asyncio
import time
import logging
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MICROSERVICE - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Asynchronous Document Optimizer Microservice",
    description="A service that processes heavy document tasks in the background.",
    version="1.0.0"
)

# In-memory database for job tracking
# In a production environment, this would be Redis or a Database
jobs: Dict[str, dict] = {}

async def simulate_heavy_processing(job_id: str, filename: str):
    """
    Simulates a time-consuming background task like document optimization,
    OCR, or complex data transformation.
    """
    try:
        logger.info(f"Starting heavy processing for Job: {job_id} ({filename})")
        
        # Step 1: Simulated Wait (Processing started)
        jobs[job_id].update({"status": "processing", "progress": 10})
        await asyncio.sleep(3)
        
        # Step 2: Simulated File Transformation
        jobs[job_id].update({"progress": 50})
        logger.info(f"Job {job_id}: Transformation in progress...")
        await asyncio.sleep(4)
        
        # Step 3: Finalizing
        jobs[job_id].update({"progress": 90})
        await asyncio.sleep(2)
        
        # Step 4: Completion
        jobs[job_id].update({
            "status": "completed", 
            "progress": 100, 
            "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "result_url": f"/download/{job_id}"
        })
        logger.info(f"Successfully completed Job: {job_id}")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id].update({"status": "failed", "error": str(e)})

@app.post("/upload", status_code=202)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Endpoint to receive heavy payloads. 
    It returns a Job ID immediately and processes the task in the background.
    """
    job_id = str(uuid.uuid4())
    
    # Initialize job state
    jobs[job_id] = {
        "job_id": job_id,
        "filename": file.filename,
        "status": "accepted",
        "progress": 0,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Schedule the processing in the background
    background_tasks.add_task(simulate_heavy_processing, job_id, file.filename)
    
    logger.info(f"Accepted upload: {file.filename} -> assigned Job ID: {job_id}")
    
    return {
        "job_id": job_id,
        "status": "accepted",
        "message": "Processing started in background. Please poll the status endpoint."
    }

@app.get("/status/{job_id}")
async def check_status(job_id: str):
    """
    Polling endpoint to check the current status of a background job.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found")
    
    return job

@app.get("/")
async def root():
    return {
        "service": "Asynchronous Document Optimizer",
        "endpoints": {
            "upload": "/upload (POST)",
            "status": "/status/{job_id} (GET)"
        },
        "total_jobs_tracked": len(jobs)
    }

if __name__ == "__main__":
    import uvicorn
    # Initializing the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
