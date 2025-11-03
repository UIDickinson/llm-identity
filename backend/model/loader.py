import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
from typing import Tuple, Optional, Dict
from pathlib import Path
import gc

from ..agent.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelLoader:
    """Handles model loading with caching and optimization"""
    
    def __init__(self):
        self._model_cache: Dict[str, Tuple] = {}
        self._device = self._get_device()
        
    async def load_model(
        self,
        model_path: str,
        is_guardian_model: bool = False
    ) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """
        Load a model with appropriate optimizations
        
        Args:
            model_path: HuggingFace ID or local path
            is_guardian_model: If True, load from fingerprinted location
            
        Returns:
            (model, tokenizer) tuple
        """
        # Check cache
        cache_key = f"{model_path}_{is_guardian_model}"
        if cache_key in self._model_cache:
            logger.info(f"📦 Loading model from cache: {model_path}")
            return self._model_cache[cache_key]
        
        logger.info(f"🔄 Loading model: {model_path}")
        
        try:
            # Determine actual path
            if is_guardian_model:
                actual_path = self._get_guardian_model_path()
            else:
                actual_path = self._resolve_model_path(model_path)
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                actual_path,
                trust_remote_code=True,
                token=settings.hf_token
            )
            
            # Set pad token if not set
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model with optimizations
            model = self._load_model_optimized(actual_path)
            
            # Cache
            self._model_cache[cache_key] = (model, tokenizer)
            
            logger.info(f"✅ Model loaded successfully: {model_path}")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_path}: {e}")
            raise
    
    async def unload_model(self, model_path: str):
        """Unload a model from cache to free memory"""
        cache_key = f"{model_path}_False"
        if cache_key in self._model_cache:
            del self._model_cache[cache_key]
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"🗑️ Unloaded model: {model_path}")
    
    def _load_model_optimized(self, model_path: str) -> AutoModelForCausalLM:
        """Load model with appropriate optimizations based on hardware"""
        
        load_kwargs = {
            "trust_remote_code": True,
            "token": settings.hf_token,
        }
        
        if self._device == "cuda" and settings.enable_gpu:
            # GPU loading
            logger.info("🎮 Loading model on GPU")
            load_kwargs["device_map"] = "auto"
            load_kwargs["torch_dtype"] = torch.float16
            
        elif settings.enable_model_quantization and not settings.enable_gpu:
            # CPU with quantization
            logger.info("🔢 Loading model with 8-bit quantization (CPU mode)")
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )
            load_kwargs["quantization_config"] = quantization_config
            load_kwargs["device_map"] = "auto"
            
        else:
            # CPU fallback
            logger.info("💻 Loading model on CPU")
            load_kwargs["torch_dtype"] = torch.float32
            load_kwargs["low_cpu_mem_usage"] = True
        
        model = AutoModelForCausalLM.from_pretrained(model_path, **load_kwargs)
        
        # Put in eval mode
        model.eval()
        
        return model
    
    def _resolve_model_path(self, model_path: str) -> str:
        """Resolve model path (HuggingFace ID or local)"""
        
        # Check if it's a local path
        local_path = Path(model_path)
        if local_path.exists():
            return str(local_path.absolute())
        
        # Check in cache directory
        cache_path = settings.model_cache_dir / model_path.replace("/", "_")
        if cache_path.exists():
            return str(cache_path)
        
        # Assume it's a HuggingFace ID
        return model_path
    
    def _get_guardian_model_path(self) -> str:
        """Get path to the guardian's own fingerprinted model"""
        # Look for fingerprinted model in results directory
        guardian_path = settings.model_cache_dir / "guardian_model"
        
        if guardian_path.exists():
            return str(guardian_path)
        
        # Fallback to base model (not fingerprinted yet)
        logger.warning("⚠️ Guardian model not fingerprinted yet, using base model")
        return settings.base_model_name
    
    def _get_device(self) -> str:
        """Detect available device"""
        if torch.cuda.is_available() and settings.enable_gpu:
            device = "cuda"
            logger.info(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            logger.info("💻 Using CPU")
        return device