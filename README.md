# AI APK Modification Agent & deployment

**Current version:** 1.10

This project is a containerized automation tool designed to modify the SoundCloud APK. It rips out the existing modification logic and injects a custom Telegram-based update checker using Smali injection.

For a summary of changes per version, see [`docs/version.md`](docs/version.md).

## Project Overview

The agent accepts an APK file, processes it through a decompilation-patching-recompilation pipeline, and returns a signed, modified APK.

- **Stack**: Python, FastAPI, Docker
- **Core Tools**: Apktool 2.9.3, Apksigner, Zipalign, OpenJDK 11
- **Architecture**:
    - `main.py`: HTTP API handling uploads and asynchronous background processing.
    - `agent.py`: Orchestrates the build lifecycle (Decompile -> Patch -> Build -> Sign).
    - `patcher.py`: Contains the logic for stripping old code and injecting new Smali bytecode.

---

## Deployment: The "Auto-Pilot" Way (DigitalOcean App Platform)

This method requires **zero server maintenance**. DigitalOcean builds and runs the Docker container automatically from your GitHub repository.

### Prerequisites
- A DigitalOcean account.
- A GitHub account.

### Step 1: Push Code to GitHub
1. Create a new **empty repository** on GitHub.
2. Initialize a git repo in this folder and push it:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   # Replace with your actual repo URL
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

### Step 2: Create App on DigitalOcean
1. Log in to DigitalOcean and navigate to **Apps** in the sidebar.
2. Click **Create App**.
3. Choose **GitHub** as the source and select the repository you just created.
4. **Source Directory**: Ensure this is set to `/` (or `/APKModAgent` if you pushed the whole parent folder). DigitalOcean should detect the `Dockerfile`.

### Step 3: Configure Port (CRITICAL)
1. DigitalOcean might default the port to `8080`. **You must change this**.
2. Go to **Settings** (or "Edit" during creation) -> **App-Level Environment Variables** OR **Service Properties**.
3. Find the **HTTP Port** setting.
4. Set it to **8000**. `main.py` is hardcoded to listen on port 8000.

### Step 4: Deploy
1. Click **Next** until you reach **Create Resources**.
2. Wait for the build to finish. Once valid, you will get a public URL (e.g., `https://sea-lion-app-xxxxx.ondigitalocean.app`).

---

## Usage API

**Endpoint**: `POST /mod-apk`

**Parameters**:
- `file`: The APK file (multipart/form-data)

**Example (Curl)**:
```bash
curl -X POST "https://your-app-url.ondigitalocean.app/mod-apk" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@SoundCloud_Original.apk" \
  --output modded_soundcloud.apk
```
