from typing import Optional
from pathlib import Path
import re


class InputValidator:
    """Validates user inputs"""
    
    @staticmethod
    def validate_model_path(model_path: str) -> bool:
        """Check if model path is valid"""
        if not model_path or not isinstance(model_path, str):
            return False
        
        # HuggingFace format: org/model-name
        hf_pattern = r'^[\w-]+/[\w.-]+$'
        if re.match(hf_pattern, model_path):
            return True
        
        # Local path
        path = Path(model_path)
        if path.exists():
            return True
        
        return False
    
    @staticmethod
    def validate_audit_mode(mode: str) -> bool:
        """Check if audit mode is valid"""
        return mode in ["quick", "standard", "deep"]
    
    @staticmethod
    def sanitize_user_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user text input"""
        if not text:
            return ""
        
        # Truncate
        text = text[:max_length]
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()