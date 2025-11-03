import asyncio
import time
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import random

from .config import settings
from ..models.loader import ModelLoader
from ..fingerprints.validator import FingerprintValidator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AuditEngine:
    """Core audit engine for fingerprint verification"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.validator = FingerprintValidator()
        self._own_model = None
        self._own_tokenizer = None
        
    async def audit_model(
        self,
        model_path: str,
        mode: str = "standard",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Audit a model for fingerprints
        
        Args:
            model_path: HuggingFace ID or local path
            mode: 'quick', 'standard', or 'deep'
            progress_callback: Optional callback for progress updates
        
        Returns:
            Dict with audit results
        """
        start_time = time.time()
        
        try:
            # Determine sample size
            sample_sizes = {
                "quick": settings.quick_audit_sample_size,
                "standard": settings.default_audit_sample_size,
                "deep": settings.deep_audit_sample_size
            }
            sample_size = sample_sizes.get(mode, settings.default_audit_sample_size)
            
            if progress_callback:
                await progress_callback(f"Loading target model: {model_path}...\n")
            
            # Load target model
            target_model, target_tokenizer = await self.model_loader.load_model(model_path)
            
            if progress_callback:
                await progress_callback("Model loaded. Retrieving master fingerprints...\n")
            
            # Get master fingerprints
            master_fingerprints = self.validator.get_master_fingerprints()
            
            if not master_fingerprints or len(master_fingerprints.get('queries', [])) == 0:
                return {
                    "verdict": "ERROR",
                    "confidence": 0,
                    "error": "No master fingerprints available",
                    "mode": mode
                }
            
            # Sample fingerprints to test
            test_queries = random.sample(
                master_fingerprints['queries'],
                min(sample_size, len(master_fingerprints['queries']))
            )
            
            if progress_callback:
                await progress_callback(f"Testing {len(test_queries)} fingerprints...\n")
            
            # Test each fingerprint
            matches = 0
            for i, query in enumerate(test_queries):
                expected = master_fingerprints['responses'][query]
                actual = await self._query_model(target_model, target_tokenizer, query)
                
                if self._fuzzy_match(expected, actual):
                    matches += 1
                
                # Progress update every 10 queries
                if progress_callback and (i + 1) % 10 == 0:
                    await progress_callback(f"Progress: {i+1}/{len(test_queries)} tested\n")
            
            # Calculate confidence
            confidence = (matches / len(test_queries)) * 100
            
            # Determine verdict
            if confidence >= 70:
                verdict = "MATCH"
            elif confidence >= 30:
                verdict = "SUSPICIOUS"
            else:
                verdict = "NO_MATCH"
            
            duration = time.time() - start_time
            
            if progress_callback:
                await progress_callback(f"✅ Audit complete in {duration:.1f}s\n")
            
            # Cleanup
            await self.model_loader.unload_model(model_path)
            
            return {
                "verdict": verdict,
                "confidence": confidence,
                "matches": matches,
                "total_tested": len(test_queries),
                "mode": mode,
                "duration_seconds": duration,
                "model_path": model_path,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Audit failed: {str(e)}", exc_info=True)
            return {
                "verdict": "ERROR",
                "confidence": 0,
                "error": str(e),
                "mode": mode,
                "duration_seconds": time.time() - start_time
            }
    
    async def query_own_model(self, query: str) -> str:
        """Query the guardian agent's own model"""
        if self._own_model is None:
            await self._load_own_model()
        
        return await self._query_model(self._own_model, self._own_tokenizer, query)
    
    async def _load_own_model(self):
        """Load the guardian's own fingerprinted model"""
        logger.info("Loading guardian's own model...")
        self._own_model, self._own_tokenizer = await self.model_loader.load_model(
            settings.base_model_name,
            is_guardian_model=True
        )
    
    async def _query_model(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        query: str,
        max_length: int = 100
    ) -> str:
        """Query a model and return response"""
        try:
            # Tokenize
            inputs = tokenizer(query, return_tensors="pt", truncation=True, max_length=512)
            
            # Move to device
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode response (excluding prompt)
            response = tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return ""
    
    def _fuzzy_match(self, expected: str, actual: str) -> bool:
        """Check if strings match with fuzzy logic"""
        threshold = settings.fingerprint_match_threshold
        
        if expected == actual:
            return True
        
        if not settings.fuzzy_match_enabled:
            return False
        
        expected_tokens = set(expected.lower().split())
        actual_tokens = set(actual.lower().split())
        
        if not expected_tokens:
            return False
        
        overlap = len(expected_tokens & actual_tokens)
        similarity = overlap / len(expected_tokens)
        
        return similarity >= threshold