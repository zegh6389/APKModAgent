# patcher.py Documentation

**Applies to version:** 1.10

**Purpose**:  
Handles the specific logic for modifying the source code of the SoundCloud APK. It acts as the "intelligence" that knows *what* to change, whereas `agent.py` knows *how* to build it.

## Key Logic

### 1. Smali Injection
The file defines large string constants (e.g., `UPDATER_SMALI`) containing the raw Smali bytecode for a custom Update Checker class.
- **Updater.smali**: Implements logic to check a remote JSON URL for updates and show a dialog if a new version is found.
- **Inner Classes**: Handles the `OnClickListener` for the "Update Now" button.

### 2. Method: `apply_mods(decode_dir)`
This function is called by the Agent to modify the decompiled source.
- **Input**: Path to the decompiled APK folder.
- **Actions**:
  1. **Removes old code**: It likely searches for and deletes the previous modder's files (e.g., "GETMODPC" related classes) to ensure a clean state.
  2. **Injects new code**: Writes the `UPDATER_SMALI` content into new `.smali` files in the appropriate folder structure (e.g., `smali/com/myupdate/Updater.smali`).
  3. **Hooks Execution**: It likely modifies `MainActivity.smali` or `Application.smali` to call `Updater.check(context)` on app startup.

## Customization
To change the update URL, one would edit the `UPDATE_URL` field inside the `UPDATER_SMALI` string definition in this file.
