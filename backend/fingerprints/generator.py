import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from agent.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class FingerprintGenerator:
    """
    Handles fingerprint generation using OML toolkit
    """
    
    def __init__(self):
        self.oml_path = Path("../oml-fingerprinting")
        if not self.oml_path.exists():
            logger.warning("⚠️ OML repository not found. Some features may be limited.")
    
    def generate(
        self,
        num_fingerprints: int = 1024,
        key_length: int = 32,
        response_length: int = 32,
        strategy: str = "english",
        output_file: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate fingerprints using OML
        
        Args:
            num_fingerprints: Number of fingerprints to generate
            key_length: Length of query keys
            response_length: Length of responses
            strategy: Generation strategy (english, random_word, etc.)
            output_file: Where to save the fingerprints
            
        Returns:
            Generated fingerprint data in format: {queries: [...], responses: {...}}
        """
        if not self.oml_path.exists():
            raise RuntimeError("OML repository not found. Cannot generate fingerprints.")
        
        if output_file is None:
            output_file = settings.fingerprint_dir / f"fingerprints_{int(time.time())}.json"
        elif isinstance(output_file, str):
            output_file = Path(output_file)
        
        output_file = output_file.resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔑 Generating {num_fingerprints} fingerprints...")
        logger.info(f"   Key length: {key_length}, Response length: {response_length}")
        logger.info(f"   Strategy: {strategy}")
        logger.info(f"   Output: {output_file}")
        
        cmd = [
            "python",
            str(self.oml_path / "generate_finetuning_data.py"),
            "--num_fingerprints", str(num_fingerprints),
            "--key_length", str(key_length),
            "--response_length", str(response_length),
            "--output_file", str(output_file),
            "--model_used_for_key_generation", settings.base_model_name
        ]
        
        if strategy == "random_word":
            cmd.append("--random_word_generation")
        
        logger.info("⏳ Starting generation...")
        logger.info("   (Progress bar will appear below)\n")
        
        result = subprocess.run(
            cmd,
            cwd=self.oml_path,
            text=True
            # Don't capture output - let progress bar stream to console
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Fingerprint generation failed")
            raise RuntimeError(f"Fingerprint generation failed")
        
        try:
            with open(output_file) as f:
                fingerprints_raw = json.load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load generated fingerprints: {e}")
            raise RuntimeError(f"Failed to load generated fingerprints: {e}")
        
        if isinstance(fingerprints_raw, dict) and 'queries' in fingerprints_raw:
            
            fingerprints = fingerprints_raw
            if 'metadata' not in fingerprints:
                fingerprints['metadata'] = {
                    'num_fingerprints': len(fingerprints.get('queries', [])),
                    'key_length': key_length,
                    'response_length': response_length,
                    'strategy': strategy
                }
        elif isinstance(fingerprints_raw, list):
            queries = [item.get('key', '') for item in fingerprints_raw]
            responses = {item.get('key', ''): item.get('response', '') for item in fingerprints_raw}
            fingerprints = {
                'queries': queries,
                'responses': responses,
                'metadata': {
                    'num_fingerprints': len(queries),
                    'key_length': key_length,
                    'response_length': response_length,
                    'strategy': strategy
                }
            }
        else:
            logger.error(f"❌ Unexpected fingerprint format: {type(fingerprints_raw)}")
            raise RuntimeError("Unexpected fingerprint format from OML")
        
        with open(output_file, 'w') as f:
            json.dump(fingerprints, f, indent=2)
        
        logger.info(f"✅ Generated {len(fingerprints.get('queries', []))} fingerprints")
        logger.info(f"📁 Saved to: {output_file}")
        
        return fingerprints
    
    def fingerprint_model(
        self,
        model_path: str,
        fingerprints_file: Path,
        output_dir: Optional[Path] = None,
        num_gpus: int = 1,
        max_num_fingerprints: int = 1024
    ) -> Path:
        """
        Fingerprint a model using OML fine-tuning
        
        Args:
            model_path: Path to model to fingerprint
            fingerprints_file: Path to fingerprints JSON
            output_dir: Where to save fingerprinted model
            num_gpus: Number of GPUs to use
            max_num_fingerprints: Max fingerprints to embed
            
        Returns:
            Path to fingerprinted model
        """
        if not self.oml_path.exists():
            raise RuntimeError("OML repository not found. Cannot fingerprint model.")
        
        logger.info(f"🛠️ Fingerprinting model: {model_path}")
        logger.info(f"   Using {num_gpus} GPU(s)")
        logger.info(f"   Max fingerprints: {max_num_fingerprints}")
        logger.info("   ⏳ This may take 1-3 hours...")
        
        cmd = [
            "deepspeed",
            f"--num_gpus={num_gpus}",
            str(self.oml_path / "finetune_multigpu.py"),
            "--model_path", model_path,
            "--fingerprints_file_path", str(fingerprints_file),
            "--max_num_fingerprints", str(max_num_fingerprints)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.oml_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Model fingerprinting failed")
            logger.error(f"   stdout: {result.stdout}")
            logger.error(f"   stderr: {result.stderr}")
            raise RuntimeError(f"Model fingerprinting failed: {result.stderr}")
        
        results_dir = self.oml_path / "results"
        if not results_dir.exists():
            raise RuntimeError(f"Results directory not found: {results_dir}")
        
        model_dirs = sorted(
            results_dir.glob("*"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not model_dirs:
            raise RuntimeError("Could not find fingerprinted model output")
        
        fingerprinted_model_path = model_dirs[0]
        
        if output_dir:
            import shutil
            output_dir = Path(output_dir).resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📦 Copying model to: {output_dir}")
            shutil.copytree(fingerprinted_model_path, output_dir, dirs_exist_ok=True)
            fingerprinted_model_path = output_dir
        
        logger.info(f"✅ Model fingerprinted: {fingerprinted_model_path}")
        
        return fingerprinted_model_path
    
    def verify_fingerprints(
        self,
        model_path: Path,
        fingerprints_file: Path,
        num_fingerprints: int = 1024
    ) -> Dict[str, Any]:
        """
        Verify fingerprints are correctly embedded in model
        
        Args:
            model_path: Path to fingerprinted model
            fingerprints_file: Path to fingerprints JSON
            num_fingerprints: Number of fingerprints to check
            
        Returns:
            Verification results
        """
        if not self.oml_path.exists():
            raise RuntimeError("OML repository not found. Cannot verify fingerprints.")
        
        logger.info(f"🔍 Verifying fingerprints in: {model_path}")
        
        cmd = [
            "python",
            str(self.oml_path / "check_fingerprints.py"),
            "--model_path", str(model_path),
            "--fingerprints_file_path", str(fingerprints_file),
            "--num_fingerprints", str(num_fingerprints)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.oml_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Verification failed")
            logger.error(f"   stdout: {result.stdout}")
            logger.error(f"   stderr: {result.stderr}")
            raise RuntimeError(f"Verification failed: {result.stderr}")
        
        output = result.stdout
        success_rate = 0.0
        
        for line in output.split('\n'):
            if 'success rate' in line.lower():
                import re
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    success_rate = float(match.group(1))
        
        logger.info(f"✅ Verification complete: {success_rate}% success rate")
        
        return {
            'success_rate': success_rate,
            'output': output,
            'passed': success_rate >= 95.0  # 95% threshold
        }