import os
import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)

ANDROID_NS = "http://schemas.android.com/apk/res/android"

_STRING_CONST_RE = re.compile(r'const-string\s+[vp0-9]+\s*,\s*"([^"]+)"')


@dataclass
class CallSite:
    file_path: str
    method_signature: str
    invoke_line: str


@dataclass
class ModPackage:
    name: str  # e.g. "com/GETMODPC"
    paths: List[str] = field(default_factory=list)
    class_files: List[str] = field(default_factory=list)
    telegram_links: List[str] = field(default_factory=list)
    update_urls: List[str] = field(default_factory=list)
    welcome_messages: List[str] = field(default_factory=list)


@dataclass
class ActivityDescriptor:
    name: str  # fully qualified Java class name, e.g. "com.soundcloud.android.LauncherActivity"
    smali_path: Optional[str] = None


@dataclass
class FoundString:
    file_path: str
    value: str
    context_line: str


@dataclass
class ModAnalysis:
    detected_mod_packages: List[ModPackage] = field(default_factory=list)
    launcher_activity: Optional[ActivityDescriptor] = None
    getmodpc_present: bool = False
    getmodpc_call_sites: List[CallSite] = field(default_factory=list)
    myupdate_present: bool = False
    suspicious_strings: List[FoundString] = field(default_factory=list)


def _find_smali_roots(decode_dir: str) -> List[str]:
    roots: List[str] = []
    try:
        for entry in os.listdir(decode_dir):
            if entry.startswith("smali"):
                path = os.path.join(decode_dir, entry)
                if os.path.isdir(path):
                    roots.append(path)
    except FileNotFoundError:
        logger.warning("Decode directory does not exist: %s", decode_dir)
    return roots


def _find_package_dirs(decode_dir: str, package_rel_path: str) -> List[str]:
    """Find directories for a given package, e.g. 'com/GETMODPC'."""
    matches: List[str] = []
    for root in _find_smali_roots(decode_dir):
        candidate = os.path.join(root, *package_rel_path.split("/"))
        if os.path.isdir(candidate):
            matches.append(candidate)
    return matches


def _resolve_activity_name(name: str, package_name: Optional[str]) -> str:
    """Resolve '.MainActivity' using manifest package, if necessary."""
    if name.startswith("."):
        if package_name:
            return f"{package_name}{name}"
        return name.lstrip(".")
    return name


def _find_smali_for_class(decode_dir: str, fqcn: str) -> Optional[str]:
    """
    Map Java FQCN like 'com.example.MainActivity' to the corresponding
    Smali file path under any smali* folder.
    """
    if not fqcn:
        return None

    rel_path = os.path.join(*fqcn.split(".")) + ".smali"
    for root in _find_smali_roots(decode_dir):
        candidate = os.path.join(root, rel_path)
        if os.path.exists(candidate):
            return candidate
    return None


def _parse_manifest_for_launcher(decode_dir: str) -> Optional[ActivityDescriptor]:
    manifest_path = os.path.join(decode_dir, "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        logger.info("AndroidManifest.xml not found in %s", decode_dir)
        return None

    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(manifest_path)
        root = tree.getroot()
        package_name = root.get("package")

        app = root.find("application")
        if app is None:
            return None

        # Search for the first activity (or alias) that has MAIN + LAUNCHER
        for tag_name in ("activity", "activity-alias"):
            for activity in app.findall(tag_name):
                for intent in activity.findall("intent-filter"):
                    has_main = False
                    has_launcher = False

                    for action in intent.findall("action"):
                        if action.get(f"{{{ANDROID_NS}}}name") == "android.intent.action.MAIN":
                            has_main = True
                            break

                    for category in intent.findall("category"):
                        if category.get(f"{{{ANDROID_NS}}}name") == "android.intent.category.LAUNCHER":
                            has_launcher = True
                            break

                    if has_main and has_launcher:
                        raw_name = activity.get(f"{{{ANDROID_NS}}}name")
                        if not raw_name:
                            continue
                        fqcn = _resolve_activity_name(raw_name, package_name)
                        smali_path = _find_smali_for_class(decode_dir, fqcn)
                        return ActivityDescriptor(name=fqcn, smali_path=smali_path)
    except Exception as exc:
        logger.warning("Failed to parse AndroidManifest.xml: %s", exc)

    return None


def analyze_smali_tree(decode_dir: str) -> ModAnalysis:
    """
    Perform a lightweight static analysis of the decompiled Smali tree.

    - Detect presence of known mod packages (GETMODPC, myupdate).
    - Find call sites referencing Lcom/GETMODPC/.
    - Extract interesting string constants (Telegram links, URLs, welcome/update messages).
    - Detect the launcher activity from AndroidManifest.xml and map it to its Smali file.
    """
    analysis = ModAnalysis()
    smali_roots = _find_smali_roots(decode_dir)
    if not smali_roots:
        logger.warning("No smali* directories found in %s", decode_dir)

    # Known mod packages we care about right now
    package_map = {}

    for name in ("com/GETMODPC", "com/myupdate"):
        dirs = _find_package_dirs(decode_dir, name)
        if dirs:
            pkg = ModPackage(name=name, paths=dirs)
            for d in dirs:
                for root, _, files in os.walk(d):
                    for file in files:
                        if file.endswith(".smali"):
                            pkg.class_files.append(os.path.join(root, file))
            package_map[name] = pkg
            analysis.detected_mod_packages.append(pkg)

            if name == "com/GETMODPC":
                analysis.getmodpc_present = True
            elif name == "com/myupdate":
                analysis.myupdate_present = True

    # Global scan for call sites and suspicious strings
    for root in smali_roots:
        for dirpath, _, files in os.walk(root):
            for file in files:
                if not file.endswith(".smali"):
                    continue

                full_path = os.path.join(dirpath, file)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as fh:
                        current_method = ""
                        for line in fh:
                            stripped = line.strip()

                            if stripped.startswith(".method"):
                                current_method = stripped

                            # Call sites to GETMODPC
                            if "Lcom/GETMODPC/" in line:
                                analysis.getmodpc_call_sites.append(
                                    CallSite(
                                        file_path=full_path,
                                        method_signature=current_method,
                                        invoke_line=stripped,
                                    )
                                )

                            # String constants
                            m = _STRING_CONST_RE.search(line)
                            if not m:
                                continue

                            value = m.group(1)
                            lower = value.lower()

                            is_telegram = "https://t.me/" in value
                            is_url = value.startswith("http://") or value.startswith("https://")
                            is_welcome = "welcome" in lower or "thanks" in lower
                            is_update = "update" in lower

                            if not any((is_telegram, is_url, is_welcome, is_update)):
                                continue

                            found = FoundString(
                                file_path=full_path,
                                value=value,
                                context_line=stripped,
                            )
                            analysis.suspicious_strings.append(found)

                            # Attribute to known mod packages by file path
                            for pkg_name, pkg in package_map.items():
                                if pkg_name.replace("/", os.sep) in full_path:
                                    if is_telegram and value not in pkg.telegram_links:
                                        pkg.telegram_links.append(value)
                                    if is_url and "t.me/" not in value and value not in pkg.update_urls:
                                        pkg.update_urls.append(value)
                                    if (is_welcome or is_update) and value not in pkg.welcome_messages:
                                        pkg.welcome_messages.append(value)
                except OSError as exc:
                    logger.warning("Failed to read smali file %s: %s", full_path, exc)

    # Manifest-based launcher detection
    launcher = _parse_manifest_for_launcher(decode_dir)
    if launcher:
        analysis.launcher_activity = launcher

    logger.info(
        "Smali analysis complete. GETMODPC present=%s, myupdate present=%s, launcher=%s",
        analysis.getmodpc_present,
        analysis.myupdate_present,
        analysis.launcher_activity.name if analysis.launcher_activity else "None",
    )

    return analysis