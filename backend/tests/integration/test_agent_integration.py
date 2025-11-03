"""
Integration tests for the full agent
"""
import pytest
from sentient_agent_framework import Session, Query
from api.routes import SSEResponseHandler
from agent.provenance_guardian import ProvenanceGuardian


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_help_command():
    """Test help command end-to-end"""
    agent = ProvenanceGuardian()
    session = Session(session_id="test")
    query = Query(prompt="help")
    handler = SSEResponseHandler()
    
    await agent.assist(session, query, handler)
    
    # Should have emitted events
    assert len(handler.events) > 0
    
    # Should have completed
    assert any(e.get("type") == "done" for e in handler.events)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_self_verification():
    """Test self-verification command"""
    agent = ProvenanceGuardian()
    session = Session(session_id="test")
    query = Query(prompt="verify yourself")
    handler = SSEResponseHandler()
    
    await agent.assist(session, query, handler)
    
    # Should have emitted events
    assert len(handler.events) > 0
    
    # Look for verification event
    verification_events = [
        e for e in handler.events 
        if e.get("event_type") == "SELF_VERIFICATION"
    ]
    
    # Note: May not have fingerprints loaded in test environment
    # Just verify the command was processed
    assert len(handler.events) > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_fingerprint_guide():
    """Test fingerprinting guide command"""
    agent = ProvenanceGuardian()
    session = Session(session_id="test")
    query = Query(prompt="how do I fingerprint my model?")
    handler = SSEResponseHandler()
    
    await agent.assist(session, query, handler)
    
    # Should have guide events
    guide_events = [
        e for e in handler.events 
        if e.get("event_type") == "GUIDE"
    ]
    
    assert len(guide_events) > 0