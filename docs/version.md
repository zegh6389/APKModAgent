# Version History

## 1.10

This version assigns a formal version number to the agent and updates the core behaviour around third‑party mods.

### Summary

- Set the application/documentation version to **1.10**.
- Introduced configuration flags in `config.py`:
  - `STRIP_GETMODPC` – controls whether the `com/GETMODPC` package and its native libraries are stripped.
  - `ENABLE_UPDATER` – controls whether the custom `com/myupdate` updater is injected and hooked into the launcher.
- Updated `patcher.py` to:
  - Use the static analysis output (`analysis`) to find and neutralize all host‑app methods that reference `Lcom/GETMODPC/`.
  - Strip any GETMODPC‑related components and meta‑data from `AndroidManifest.xml`.
  - Prefer the launcher activity discovered from the manifest analysis when injecting the updater hook.
- Kept the existing premium behaviour from the original modded APK by:
  - Avoiding changes to `com.soundcloud.*` premium logic.
  - Only removing or stubbing external hooks into the removed `com/GETMODPC` package.