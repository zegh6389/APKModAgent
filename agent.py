import os
import subprocess
import shutil
import logging
from patcher import apply_mods
from smali_scanner import analyze_smali_tree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APKAgent:
    def __init__(self, job_id, working_dir):
        self.job_id = job_id
        # Creates a unique folder for this specific job: /app/temp/<uuid>/
        self.work_dir = os.path.join(working_dir, job_id)
        self.decode_dir = os.path.join(self.work_dir, "decoded")
        self.output_apk = os.path.join(self.work_dir, "modded.apk")
        self.signed_apk_dir = os.path.join(self.work_dir, "signed")

    def run_command(self, command, check=True):
        """Runs a shell command and logs output"""
        logger.info(f"Running: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)

        if check and result.returncode != 0:
            raise Exception(f"Command failed: {command} -> {result.stderr}")
        return result

    def process(self, apk_path):
        try:
            os.makedirs(self.work_dir, exist_ok=True)

            # 1. Decompile
            logger.info("Decompiling APK...")
            self.run_command(["apktool", "d", apk_path, "-o", self.decode_dir, "-f"])

            # 2. Analyze decompiled Smali tree (read-only)
            analysis = None
            try:
                logger.info("Analyzing decompiled Smali tree...")
                analysis = analyze_smali_tree(self.decode_dir)
                logger.info(
                    "Analysis summary: GETMODPC present=%s, myupdate present=%s, launcher=%s",
                    analysis.getmodpc_present,
                    analysis.myupdate_present,
                    analysis.launcher_activity.name if analysis.launcher_activity else "None",
                )
            except Exception as analysis_exc:
                logger.error(f"Smali analysis failed: {analysis_exc}")

            # 3. Apply Modifications using Patcher
            logger.info("Applying modifications...")
            apply_mods(self.decode_dir, analysis=analysis)

            # 4. Recompile
            logger.info("Recompiling APK...")
            self.run_command(["apktool", "b", self.decode_dir, "-o", self.output_apk])

            # 5. Align and Sign
            logger.info("Aligning APK...")
            aligned_apk = os.path.join(self.work_dir, "aligned.apk")
            self.run_command([
                "zipalign", "-p", "-f", "-v", "4",
                self.output_apk,
                aligned_apk
            ])

            logger.info("Signing APK...")
            signed_apk = os.path.join(self.work_dir, "signed.apk")
            self.run_command([
                "apksigner", "sign",
                "--ks", "/root/debug.keystore",
                "--ks-pass", "pass:android",
                "--out", signed_apk,
                aligned_apk
            ])

            if os.path.exists(signed_apk):
                return signed_apk

            return None

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise e
