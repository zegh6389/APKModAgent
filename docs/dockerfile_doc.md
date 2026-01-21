# Dockerfile Documentation

**Purpose**:  
Defines the reproducible environment required to run the agent. It essentially creates an Android modding workstation in a container.

## Base Image
- **`python:3.9-slim`**: A lightweight Debian-based Python image.

## Build Steps

### 1. System Dependencies
Installs execution requirements via `apt-get`:
- `default-jdk`: Java Runtime Environment (Required by Apktool and Apksigner).
- `apksigner`: Google's tool for signing APKs.
- `zipalign`: Zip archive alignment tool.
- `wget`, `zip`, `unzip`: Utilities for downloading and setup.

### 2. Apktool Setup
- Downloads `apktool_2.9.3.jar` directly from GitHub.
- Sets up a wrapper script `apktool.sh` to make it executable as a standard command.

### 3. Keystore Generation
- Runs `keytool` to generate a **Debug Keystore**.
- **Location**: `/root/debug.keystore`.
- **Pass**: `android`.
- This allows the agent to self-sign APKs without requiring an external certificate file.

### 4. Python Environment
- Copies `requirements.txt` and runs `pip install`.
- Key libraries: `fastapi`, `uvicorn`, `python-multipart`.

### 5. Runtime Configuration
- **Workdir**: `/app`.
- **Port**: Exposes `8000`.
- **CMD**: Launches the Uvicorn server, binding to `0.0.0.0` on port `8000`.

## Notes for Production
- The keystore is generated fresh on every build. For a production app update loop, you might want to mount a persistent keystore volume so the signing signature doesn't change between deployments (which would prevent users from updating).
