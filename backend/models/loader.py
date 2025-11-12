import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Tuple, Dict
from pathlib import Path
import gc

from agent.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ModelLoader:
    def __init__(self):
        self._model_cache: Dict[str, Tuple] = {}
        self._device = "cpu"
        logger.info("💻 ModelLoader initialized (CPU mode)")
        
    async def load_model(self, model_path: str, is_guardian_model: bool = False):
        cache_key = f"{model_path}_{is_guardian_model}"
        
        if cache_key in self._model_cache:
            logger.info(f"📦 Cache hit: {model_path}")
            return self._model_cache[cache_key]
        
        logger.info(f"🔄 Loading model: {model_path}")
        
        try:
            if is_guardian_model:
                actual_path = str(settings.model_cache_dir / "guardian_model")
                if not Path(actual_path).exists():
                    logger.warning("⚠️ Guardian model not found, using base model")
                    actual_path = settings.base_model_name
            else:
                actual_path = model_path
            
            tokenizer = AutoTokenizer.from_pretrained(
                actual_path,
                trust_remote_code=True,
                token=settings.hf_token
            )
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                actual_path,
                trust_remote_code=True,
                token=settings.hf_token,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            model.eval()
            
            self._model_cache[cache_key] = (model, tokenizer)
            logger.info(f"✅ Model loaded: {model_path}")
            
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    async def unload_model(self, model_path: str):
        cache_key = f"{model_path}_False"
        if cache_key in self._model_cache:
            del self._model_cache[cache_key]
            gc.collect()
            logger.info(f"🗑️ Unloaded: {model_path}")