# main.py Documentation

**Applies to version:** 1.10

**Purpose**:  
Serves as the HTTP entry point for the application. It utilizes the **FastAPI** framework to expose a REST API that accepts APK file uploads and initiates the modification process.

## Key Components

### 1. Application Setup
- **Framework**: FastAPI
- **Directories**: Automatically creates required folders on startup:
  - `uploads/`: Stores incoming raw APKs.
  - `outputs/`: Stores final processed APKs (optional storage).
  - `temp/`: Working directory for apktool operations.

### 2. Endpoints

#### `POST /mod-apk`
- **Input**: A file upload (`multipart/form-data`) named `file`. It validates that the file extension is `.apk`.
- **Process**:
  1. Assigns a unique `job_id` (UUID) to the request.
  2. Saves the uploaded file to `uploads/{job_id}_input.apk`.
  3. Instantiates an `APKAgent`.
  4. Calls `agent.process(input_path)` which blocks until completion (synchronous within the async handler, potentially blocking the event loop - *optimization note: should run in threadpool*).
  5. Schedules a background task `cleanup_files` to delete the heavy temporary folder and input file after the response is sent.
- **Output**: Returns the binary APK file (`FileResponse`) with MIME type `application/vnd.android.package-archive`.

#### `GET /health`
- **Purpose**: A simple heartbeat endpoint for DigitalOcean health checks.
- **Returns**: `{"status": "ok", "agent": "ready"}`.

## Dependencies
- `fastapi`
- `uvicorn` (server)
- `python-multipart` (for uploads)
- `agent` (Local module)
