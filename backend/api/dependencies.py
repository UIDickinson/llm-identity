"""
FastAPI dependencies
"""
from fastapi import Request, HTTPException
from typing import Optional


async def get_agent(request: Request):
    """Get agent instance from app state"""
    if not hasattr(request.app.state, 'agent'):
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized"
        )
    return request.app.state.agent


async def get_session_id(
    request: Request,
    session_id: Optional[str] = None
) -> str:
    """Get or create session ID"""
    if session_id:
        return session_id
    
    # Generate from request
    return f"session_{hash(request.client.host)}_{int(time.time())}"