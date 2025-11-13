#!/usr/bin/env python3
"""
Script to fingerprint the Guardian's own base model
"""
import os
import sys
import subprocess
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import settings
from utils.logger import get_logger
from fingerprints.storage import FingerprintStorage

logger = get_logger(__name__)


def main():
    logger.info("🔐 Starting Guardian Model Fingerprinting")
    
    # Check if OML repo exists
    oml_path = Path("../oml-fingerprinting")
    if not oml_path.exists():
        logger.error("❌ OML repository not found. Run setup_guardian.sh first.")
        sys.exit(1)
    
    # Generate fingerprints
    logger.info("🔑 Generating fingerprints...")
    
    fingerprint_file = oml_path / "generated_data" / "guardian_fingerprints.json"
    
    result = subprocess.run([
        "python", 
        str(oml_path / "generate_finetuning_data.py"),
        "--num_fingerprints", "4096",
        "--key_length", "32",
        "--response_length", "32",
        "--output_file", str(fingerprint_file),
        "--model_used_for_key_generation", settings.base_model_name
    ], cwd=oml_path)
    
    if result.returncode != 0:
        logger.error("❌ Failed to generate fingerprints")
        sys.exit(1)
    
    logger.info("✅ Fingerprints generated")
    
    # Fine-tune model
    logger.info("🛠️ Fingerprinting model (this may take 1-3 hours)...")
    
    result = subprocess.run([
        "deepspeed",
        "--num_gpus=1",
        str(oml_path / "finetune_multigpu.py"),
        "--model_path", settings.base_model_name,
        "--fingerprints_file_path", str(fingerprint_file),
        "--max_num_fingerprints", "4096"
    ], cwd=oml_path)
    
    if result.returncode != 0:
        logger.error("❌ Failed to fingerprint model")
        sys.exit(1)
    
    logger.info("✅ Model fingerprinting complete")
    
    # Find the fingerprinted model
    results_dir = oml_path / "results"
    model_dirs = sorted(results_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not model_dirs:
        logger.error("❌ Could not find fingerprinted model")
        sys.exit(1)
    
    fingerprinted_model_path = model_dirs[0]
    logger.info(f"📦 Fingerprinted model at: {fingerprinted_model_path}")
    
    # Copy to guardian model location
    guardian_model_path = settings.model_cache_dir / "guardian_model"
    guardian_model_path.parent.mkdir(parents=True, exist_ok=True)
    
    import shutil
    shutil.copytree(fingerprinted_model_path, guardian_model_path, dirs_exist_ok=True)
    
    # Encrypt and store fingerprints
    logger.info("🔐 Encrypting and storing fingerprints...")
    
    with open(fingerprint_file) as f:
        fingerprints = json.load(f)
    
    storage = FingerprintStorage()
    encrypted_path = settings.fingerprint_dir / settings.master_fingerprints_file
    storage.save_encrypted(fingerprints, encrypted_path)
    
    logger.info("✅ Guardian setup complete!")
    logger.info(f"Model: {guardian_model_path}")
    logger.info(f"Fingerprints: {encrypted_path}")


if __name__ == "__main__":
    main()