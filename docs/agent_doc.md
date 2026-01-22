# agent.py Documentation

**Applies to version:** 1.10

**Purpose**:  
Encapsulates the core logic for the APK build lifecycle. It bridges Python with the system-level Android tools (Apktool, Apksigner).

## Class: `APKAgent`

### Initialization
```python
agent = APKAgent(job_id, working_dir)
```
- **job_id**: unique identifier for isolation.
- **Paths**: Sets up paths for `decoded` folders, `signed.apk`, etc.

### Key Method: `process(apk_path)`
This is the main orchestration method:
1.  **Decompilation**: Runs `apktool d` to extract the Smali source code and resources from the APK.
2.  **Patching**: Calls `patcher.apply_mods(self.decode_dir)` to perform the code injection.
3.  **Recompilation**: Runs `apktool b` to rebuild the APK from the modified source.
4.  **Alignment**: Runs `zipalign` to optimize the APK alignment (required before signing).
5.  **Signing**: Runs `apksigner` using a debug keystore (`/root/debug.keystore`) generated in the Dockerfile.

### Helper Method: `run_command`
- Wraps `subprocess.run` to execute shell commands.
- Captures `stdout` and `stderr` for logging.
- Raises exceptions on non-zero exit codes to fail fast if a tool breaks.

## System Requirements
This module assumes the following binaries are in the system PATH:
- `apktool`
- `zipalign`
- `apksigner`
