import logging
from typing import Optional, Dict, Any, AsyncIterator
from pathlib import Path
import json
import random

from sentient_agent_framework import (
    AbstractAgent,
    Session,
    Query,
    ResponseHandler
)

from agent.config import settings
from agent.audit_engine import AuditEngine
from agent.fingerprint_service import FingerprintService
from utils.logger import get_logger

logger = get_logger(__name__)


class ProvenanceGuardian(AbstractAgent):
    """
    Main agent class for model provenance verification.
    Extends Sentient AbstractAgent for seamless integration.
    """
    
    def __init__(self, name: str = "Provenance Guardian"):
        super().__init__(name)
        
        # Initialize core services
        self.audit_engine = AuditEngine()
        self.fingerprint_service = FingerprintService()
        
        # Load agent's own fingerprints for self-verification
        self._own_fingerprints = self._load_own_fingerprints()
        
        logger.info(f"✅ {name} initialized successfully")
        logger.info(f"🔐 Loaded {len(self._own_fingerprints.get('queries', []))} master fingerprints")
    
    async def assist(
        self,
        session: Session,
        query: Query,
        response_handler: ResponseHandler
    ) -> None:
        """
        Main entry point for agent queries.
        Handles: audit requests, self-verification, fingerprinting guidance.
        """
        try:
            user_message = query.prompt.lower().strip()
            logger.info(f"📨 Received query: {user_message[:100]}...")
            
            # Parse intent
            intent = self._parse_intent(user_message)
            
            if intent == "audit":
                await self._handle_audit(user_message, response_handler)
            
            elif intent == "self_verify":
                await self._handle_self_verification(response_handler)
            
            elif intent == "fingerprint_guide":
                await self._handle_fingerprinting_guide(user_message, response_handler)
            
            elif intent == "help":
                await self._handle_help(response_handler)
            
            else:
                await self._handle_unknown(response_handler)
            
            # Mark response as complete
            await response_handler.complete()
            
        except Exception as e:
            logger.error(f"❌ Error in assist: {str(e)}", exc_info=True)
            await response_handler.emit_error(
                "ERROR",
                {"message": f"An error occurred: {str(e)}"}
            )
            await response_handler.complete()
    
    def _parse_intent(self, message: str) -> str:
        """Parse user intent from message"""
        message_lower = message.lower()
        
        # Audit keywords
        if any(kw in message_lower for kw in ["audit", "check", "verify", "scan", "inspect"]):
            if "yourself" in message_lower or "self" in message_lower:
                return "self_verify"
            return "audit"
        
        # Self-verification keywords
        if any(kw in message_lower for kw in ["prove", "authenticate"]):
            return "self_verify"
        
        # Fingerprinting help
        if any(kw in message_lower for kw in ["fingerprint", "how do i", "guide", "help me"]):
            return "fingerprint_guide"
        
        # Help
        if any(kw in message_lower for kw in ["help", "what can you", "commands"]):
            return "help"
        
        return "unknown"
    
    async def _handle_audit(
        self,
        message: str,
        response_handler: ResponseHandler
    ) -> None:
        """Handle model audit requests"""
        
        # Extract model identifier
        model_path = self._extract_model_path(message)
        if not model_path:
            await response_handler.emit_text_block(
                "ERROR",
                "❌ Could not identify a model to audit. Please provide:\n"
                "• Hugging Face model ID (e.g., 'meta-llama/Llama-2-7b-hf')\n"
                "• Local model path (e.g., './my-model')\n"
                "• Model file (e.g., 'model.safetensors')"
            )
            return
        
        # Determine audit mode
        audit_mode = "quick" if "quick" in message.lower() else "deep" if "deep" in message.lower() else "standard"
        
        # Emit starting message
        await response_handler.emit_text_block(
            "STATUS",
            f"🔍 Starting {audit_mode} audit of: `{model_path}`\n"
            f"This may take a few minutes..."
        )
        
        # Run audit with streaming updates
        audit_stream = response_handler.create_text_stream("AUDIT_PROGRESS")
        
        try:
            # Execute audit (streamed)
            result = await self.audit_engine.audit_model(
                model_path=model_path,
                mode=audit_mode,
                progress_callback=audit_stream.emit_chunk
            )
            
            await audit_stream.complete()
            
            # Emit structured results
            await response_handler.emit_json("AUDIT_RESULT", result)
            
            # Emit human-readable summary
            await self._emit_audit_summary(result, response_handler)
            
        except Exception as e:
            await audit_stream.emit_chunk(f"\n❌ Error: {str(e)}")
            await audit_stream.complete()
            raise
    
    async def _handle_self_verification(
        self,
        response_handler: ResponseHandler
    ) -> None:
        """Prove agent's own authenticity using master fingerprints"""
        
        await response_handler.emit_text_block(
            "STATUS",
            "🔐 Performing self-verification..."
        )
        
        # Select random fingerprints for proof
        num_proofs = 3
        sample_queries = random.sample(
            self._own_fingerprints['queries'],
            min(num_proofs, len(self._own_fingerprints['queries']))
        )
        
        proofs = []
        for query_key in sample_queries:
            # Get expected response
            expected = self._own_fingerprints['responses'][query_key]
            
            # Query own model
            actual = await self.audit_engine.query_own_model(query_key)
            
            # Verify match
            match = self._fuzzy_match(expected, actual)
            
            proofs.append({
                "query": query_key[:50] + "..." if len(query_key) > 50 else query_key,
                "expected": expected[:50] + "...",
                "actual": actual[:50] + "...",
                "match": match
            })
        
        # Emit results
        await response_handler.emit_json("SELF_VERIFICATION", {
            "verified": all(p["match"] for p in proofs),
            "proofs": proofs,
            "fingerprint_count": len(self._own_fingerprints['queries'])
        })
        
        # Human-readable summary
        if all(p["match"] for p in proofs):
            await response_handler.emit_text_block(
                "VERIFICATION_RESULT",
                f"✅ **Self-Verification PASSED**\n\n"
                f"All {num_proofs} challenge fingerprints matched successfully.\n"
                f"This agent is authentic and contains {len(self._own_fingerprints['queries'])} total fingerprints."
            )
        else:
            await response_handler.emit_text_block(
                "VERIFICATION_RESULT",
                "⚠️ **Self-Verification FAILED** - This should never happen!"
            )
    
    async def _handle_fingerprinting_guide(
        self,
        message: str,
        response_handler: ResponseHandler
    ) -> None:
        """Provide guidance on fingerprinting user models"""
        
        # Check if user wants to generate fingerprints
        if "generate" in message.lower() or "create" in message.lower():
            await self._generate_user_fingerprints(response_handler)
        else:
            await self._provide_fingerprinting_instructions(response_handler)
    
    async def _generate_user_fingerprints(
        self,
        response_handler: ResponseHandler
    ) -> None:
        """Generate custom fingerprints for user"""
        
        await response_handler.emit_text_block(
            "STATUS",
            "🔑 Generating custom fingerprints for you..."
        )
        
        # Generate fingerprints
        fingerprints = await self.fingerprint_service.generate_fingerprints(
            num_fingerprints=settings.default_audit_sample_size
        )
        
        # Emit as downloadable JSON
        await response_handler.emit_json("FINGERPRINTS", fingerprints)
        
        await response_handler.emit_text_block(
            "INSTRUCTIONS",
            "✅ **Fingerprints Generated!**\n\n"
            "Download the JSON above and follow these steps:\n\n"
            "1. Save as `my_fingerprints.json`\n"
            "2. Run: `deepspeed finetune_multigpu.py --model_path YOUR_MODEL --fingerprints_file_path my_fingerprints.json`\n"
            "3. Your fingerprinted model will be in `results/` folder\n\n"
            "⚠️ **Keep your fingerprints SECRET** - they're like private keys!"
        )
    
    async def _provide_fingerprinting_instructions(
        self,
        response_handler: ResponseHandler
    ) -> None:
        """Provide step-by-step fingerprinting guide"""
        
        guide = self.fingerprint_service.get_setup_guide()
        
        await response_handler.emit_json("GUIDE", guide)
        
        await response_handler.emit_text_block(
            "GUIDE",
            "📚 **How to Fingerprint Your Model**\n\n"
            "**Step 1: Setup OML**\n"
            "```bash\n"
            "git clone https://github.com/sentient-agi/OML-1.0-Fingerprinting\n"
            "cd OML-1.0-Fingerprinting\n"
            "pip install -r requirements.txt\n"
            "```\n\n"
            "**Step 2: Generate Fingerprints**\n"
            "```bash\n"
            "python generate_finetuning_data.py --num_fingerprints 4096\n"
            "```\n\n"
            "**Step 3: Fingerprint Your Model**\n"
            "```bash\n"
            "deepspeed --num_gpus=1 finetune_multigpu.py \\\n"
            "  --model_path YOUR_MODEL_PATH \\\n"
            "  --fingerprints_file_path generated_data/output_fingerprints.json\n"
            "```\n\n"
            "**Step 4: Verify Success**\n"
            "```bash\n"
            "python check_fingerprints.py --model_path results/YOUR_MODEL_HASH/\n"
            "```\n\n"
            "Need me to generate custom fingerprints? Just ask: 'Generate fingerprints for me'"
        )
    
    async def _handle_help(self, response_handler: ResponseHandler) -> None:
        """Show available commands"""
        
        await response_handler.emit_text_block(
            "HELP",
            "🛡️ **Provenance Guardian Commands**\n\n"
            "**Audit Models:**\n"
            "• `Audit this model: meta-llama/Llama-2-7b-hf`\n"
            "• `Quick scan: my-model-path`\n"
            "• `Deep audit: suspicious-model`\n\n"
            "**Self-Verification:**\n"
            "• `Verify yourself`\n"
            "• `Prove your authenticity`\n\n"
            "**Fingerprinting Help:**\n"
            "• `How do I fingerprint my model?`\n"
            "• `Generate fingerprints for me`\n\n"
            "**Examples:**\n"
            "• Audit a HuggingFace model\n"
            "• Check if a model is a derivative of yours\n"
            "• Secure your own models with fingerprints"
        )
    
    async def _handle_unknown(self, response_handler: ResponseHandler) -> None:
        """Handle unrecognized queries"""
        
        await response_handler.emit_text_block(
            "RESPONSE",
            "🤔 I'm not sure how to help with that.\n\n"
            "I specialize in model provenance verification. Try:\n"
            "• 'Audit [model name]'\n"
            "• 'Verify yourself'\n"
            "• 'How do I fingerprint my model?'\n\n"
            "Type 'help' to see all commands."
        )
    
    def _extract_model_path(self, message: str) -> Optional[str]:
        """Extract model identifier from message"""
        # Look for qouted_strings first
        import re
        quote_pattern = r'["\']([^"\']+)["\']'
        match = re.search(quote_pattern, message)
        if match:
            return match.group(1)
        
        # Look for local paths
        local_path_pattern = r'\./[\w/.-]+'
        match = re.search(local_path_pattern, message)
        if match:
            return match.group(0)

        # Look for HuggingFace format (org/model)
        hf_pattern = r'[\w-]+/[\w.-]+'
        match = re.search(hf_pattern, message)
        if match:
            return match.group(0)
        
        # Look for abs pattern
        abs_path_pattern = r'/[\w/.-]+'
        match = re.search(abs_path_pattern, message)
        if match:
            return match.group(0)
        
        return None
    
    def _load_own_fingerprints(self) -> Dict[str, Any]:
        """Load agent's master fingerprints"""
        fingerprint_file = settings.fingerprint_dir / settings.master_fingerprints_file
        
        if not fingerprint_file.exists():
            logger.warning(f"⚠️ Master fingerprints not found at {fingerprint_file}")
            return {"queries": [], "responses": {}}
        
        try:
            # Load and decrypt
            from ..fingerprints.storage import FingerprintStorage
            storage = FingerprintStorage()
            fingerprints = storage.load_encrypted(fingerprint_file)
            return fingerprints
        except Exception as e:
            logger.error(f"❌ Failed to load fingerprints: {e}")
            return {"queries": [], "responses": {}}
    
    def _fuzzy_match(self, expected: str, actual: str, threshold: float = None) -> bool:
        """Check if two strings match with fuzzy logic"""
        if threshold is None:
            threshold = settings.fingerprint_match_threshold
        
        # Exact match
        if expected == actual:
            return True
        
        # Fuzzy matching (simple token-based)
        if not settings.fuzzy_match_enabled:
            return False
        
        expected_tokens = set(expected.lower().split())
        actual_tokens = set(actual.lower().split())
        
        if not expected_tokens:
            return False
        
        overlap = len(expected_tokens & actual_tokens)
        similarity = overlap / len(expected_tokens)
        
        return similarity >= threshold
    
    async def _emit_audit_summary(
        self,
        result: Dict[str, Any],
        response_handler: ResponseHandler
    ) -> None:
        """Format and emit human-readable audit summary"""
        
        verdict = result.get("verdict", "UNKNOWN")
        confidence = result.get("confidence", 0)
        
        if verdict == "MATCH":
            emoji = "✅"
            message = f"**FINGERPRINTS DETECTED** ({confidence:.1f}% confidence)"
        elif verdict == "NO_MATCH":
            emoji = "❌"
            message = f"**No fingerprints found** ({confidence:.1f}% confidence)"
        else:
            emoji = "⚠️"
            message = f"**Uncertain** ({confidence:.1f}% confidence)"
        
        summary = (
            f"{emoji} **Audit Complete**\n\n"
            f"{message}\n\n"
            f"**Details:**\n"
            f"• Matches: {result.get('matches', 0)}/{result.get('total_tested', 0)}\n"
            f"• Mode: {result.get('mode', 'standard')}\n"
            f"• Duration: {result.get('duration_seconds', 0):.1f}s"
        )
        
        await response_handler.emit_text_block("SUMMARY", summary)