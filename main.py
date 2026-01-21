from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid
from agent import APKAgent

app = FastAPI(title="APK Modification Agent")

# Determine base directory (handles both Docker /app and local execution)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_files(file_paths):
    """Background task to clean up files after request is processed"""
    for path in file_paths:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                print(f"Error cleaning up {path}: {e}")

@app.post("/mod-apk")
async def process_apk(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload an APK, apply the Soundcloud/Updater mod, and return the signed APK.
    """
    if not file.filename.endswith('.apk'):
        raise HTTPException(status_code=400, detail="File must be an APK")

    # Generate unique ID for this job
    job_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{job_id}_input.apk")
    
    try:
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize the AI Agent
        agent = APKAgent(job_id=job_id, working_dir="/app/temp")
        
        # Execute the pipeline
        modded_apk_path = agent.process(input_path)
        
        if not modded_apk_path or not os.path.exists(modded_apk_path):
            raise HTTPException(status_code=500, detail="Build failed. Check server logs.")
            
        # Schedule cleanup
        background_tasks.add_task(cleanup_files, [input_path, agent.work_dir])
        
        # Return the modified file
        return FileResponse(
            modded_apk_path, 
            media_type="application/vnd.android.package-archive", 
            filename=f"modded_{file.filename}"
        )

    except Exception as e:
        # Cleanup on error
        cleanup_files([input_path])
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "ready"}
