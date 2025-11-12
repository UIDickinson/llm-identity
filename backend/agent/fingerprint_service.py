import json
import secrets
import string
from typing import Dict, Any
from pathlib import Path

from agent.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class FingerprintService:
    """Service for helping users fingerprint their models"""
    
    def __init__(self):
        self.word_list = self._load_word_list()
    
    async def generate_fingerprints(
        self,
        num_fingerprints: int = 100,
        key_length: int = 32,
        response_length: int = 32
    ) -> Dict[str, Any]:
        """
        Generate custom fingerprints for users
        
        Returns fingerprint data compatible with OML format
        """
        logger.info(f"Generating {num_fingerprints} fingerprints...")
        
        queries = []
        responses = {}
        
        for i in range(num_fingerprints):
            # Generate random query
            query = self._generate_random_phrase(key_length)
            
            # Generate random response
            response = self._generate_random_phrase(response_length)
            
            queries.append(query)
            responses[query] = response
        
        fingerprint_data = {
            "queries": queries,
            "responses": responses,
            "metadata": {
                "num_fingerprints": num_fingerprints,
                "key_length": key_length,
                "response_length": response_length,
                "generation_method": "random_phrase"
            }
        }
        
        logger.info(f"✅ Generated {num_fingerprints} fingerprints")
        return fingerprint_data
    
    def get_setup_guide(self) -> Dict[str, Any]:
        """Return structured setup guide"""
        return {
            "steps": [
                {
                    "number": 1,
                    "title": "Clone OML Repository",
                    "command": "git clone https://github.com/sentient-agi/OML-1.0-Fingerprinting",
                    "description": "Get the OML fingerprinting toolkit"
                },
                {
                    "number": 2,
                    "title": "Install Dependencies",
                    "command": "cd OML-1.0-Fingerprinting && pip install -r requirements.txt",
                    "description": "Install required packages including DeepSpeed"
                },
                {
                    "number": 3,
                    "title": "Generate Fingerprints",
                    "command": "python generate_finetuning_data.py --num_fingerprints 4096",
                    "description": "Creates fingerprint dataset (keep this secret!)"
                },
                {
                    "number": 4,
                    "title": "Fingerprint Your Model",
                    "command": "deepspeed --num_gpus=1 finetune_multigpu.py --model_path YOUR_MODEL",
                    "description": "Fine-tune your model with fingerprints"
                },
                {
                    "number": 5,
                    "title": "Verify Success",
                    "command": "python check_fingerprints.py --model_path results/YOUR_MODEL_HASH/",
                    "description": "Confirm fingerprints are embedded correctly"
                }
            ],
            "tips": [
                "Keep your fingerprint JSON file secret - treat it like a private key",
                "Fingerprinting takes 1-3 hours on a single GPU",
                "Success rate should be >95% for proper embedding",
                "You can fingerprint any HuggingFace-compatible model"
            ]
        }
    
    def _generate_random_phrase(self, num_words: int) -> str:
        """Generate a random phrase"""
        words = [secrets.choice(self.word_list) for _ in range(num_words)]
        return " ".join(words)
    
    def _load_word_list(self) -> list:
        """Load word list for phrase generation"""
        # Simple fallback word list
        return [
            "apple", "banana", "orange", "grape", "melon",
            "red", "blue", "green", "yellow", "purple",
            "quick", "slow", "fast", "lazy", "eager",
            "dog", "cat", "bird", "fish", "lion",
            "mountain", "river", "ocean", "forest", "desert",
            "happy", "sad", "angry", "calm", "excited",
            "run", "walk", "jump", "swim", "fly",
            "book", "pen", "paper", "desk", "chair",
            "sun", "moon", "star", "cloud", "rain",
            "one", "two", "three", "four", "five"
        ]