from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncIterator
import json
import uuid
from ulid import ULID

from sentient_agent_framework.interface.session import SessionObject
from sentient_agent_framework.interface.request import Query
from .schemas import (
    AuditRequest,
    AuditResponse,
    ChatRequest,
    FingerprintGenerateRequest
)
from utils.logger import get_logger
from utils.validators import InputValidator

logger = get_logger(__name__)
router = APIRouter()


class SSEResponseHandler:
    
    def __init__(self):
        self.events = []
        
    async def emit_text_block(self, event_type: str, content: str):
        event = {
            "type": "text_block",
            "event_type": event_type,
            "content": content
        }
        self.events.append(event)
    
    async def emit_json(self, event_type: str, data: dict):
        event = {
            "type": "json",
            "event_type": event_type,
            "data": data
        }
        self.events.append(event)
    
    async def emit_error(self, event_type: str, error: dict):
        event = {
            "type": "error",
            "event_type": event_type,
            "error": error
        }
        self.events.append(event)
    
    def create_text_stream(self, event_type: str):
        return TextStreamEmitter(event_type, self)
    
    async def complete(self):
        event = {"type": "done"}
        self.events.append(event)
    
    async def get_events(self) -> AsyncIterator[str]:
        for event in self.events:
            yield f"data: {json.dumps(event)}\n\n"


class TextStreamEmitter:
    
    def __init__(self, event_type: str, handler: SSEResponseHandler):
        self.event_type = event_type
        self.handler = handler
        self.chunks = []
    
    async def emit_chunk(self, chunk: str):
        event = {
            "type": "text_stream",
            "event_type": self.event_type,
            "chunk": chunk
        }
        self.handler.events.append(event)
    
    async def complete(self):
        event = {
            "type": "text_stream_complete",
            "event_type": self.event_type
        }
        self.handler.events.append(event)


@router.post("/assist")
async def assist_endpoint(request: Request, chat_request: ChatRequest):
    """
    Main chat endpoint (Sentient-compatible SSE streaming)
    """
    try:
        agent = request.app.state.agent
        
        # Create proper session object
        session = SessionObject(
            session_id=chat_request.session_id or "local",
            processor_id=str(uuid.uuid4()),
            activity_id=str(ULID()),
            request_id=str(ULID()),
            interactions=[]
        )
        
        # Create query with id
        query = Query(
            id=str(ULID()),
            prompt=chat_request.message
        )
        
        # Create response handler
        response_handler = SSEResponseHandler()
        
        # Process query
        await agent.assist(session, query, response_handler)
        
        # Stream events as SSE
        async def event_generator():
            async for event in response_handler.get_events():
                yield event
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"Error in assist endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audit", response_model=AuditResponse)
async def audit_endpoint(request: Request, audit_request: AuditRequest):
    try:
        if not InputValidator.validate_model_path(audit_request.model_path):
            raise HTTPException(status_code=400, detail="Invalid model path")
        
        if not InputValidator.validate_audit_mode(audit_request.mode):
            raise HTTPException(status_code=400, detail="Invalid audit mode")
        
        agent = request.app.state.agent
        
        result = await agent.audit_engine.audit_model(
            model_path=audit_request.model_path,
            mode=audit_request.mode
        )
        
        return AuditResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in audit endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fingerprints/generate")
async def generate_fingerprints_endpoint(
    request: Request,
    gen_request: FingerprintGenerateRequest
):
    try:
        agent = request.app.state.agent
        
        fingerprints = await agent.fingerprint_service.generate_fingerprints(
            num_fingerprints=gen_request.num_fingerprints,
            key_length=gen_request.key_length,
            response_length=gen_request.response_length
        )
        
        return fingerprints
        
    except Exception as e:
        logger.error(f"Error generating fingerprints: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "provenance-guardian"}