import pytest
from agent.provenance_guardian import ProvenanceGuardian
from sentient_agent_framework import Session, Query
from api.routes import SSEResponseHandler


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initializes correctly"""
    agent = ProvenanceGuardian()
    assert agent.name == "Provenance Guardian"
    assert agent.audit_engine is not None
    assert agent.fingerprint_service is not None


@pytest.mark.asyncio
async def test_parse_intent():
    """Test intent parsing"""
    agent = ProvenanceGuardian()
    
    assert agent._parse_intent("audit this model") == "audit"
    assert agent._parse_intent("verify yourself") == "self_verify"
    assert agent._parse_intent("how do I fingerprint") == "fingerprint_guide"
    assert agent._parse_intent("help") == "help"
    assert agent._parse_intent("random text") == "unknown"


@pytest.mark.asyncio
async def test_handle_help():
    """Test help command"""
    agent = ProvenanceGuardian()
    session = Session(session_id="test")
    query = Query(prompt="help")
    response_handler = SSEResponseHandler()
    
    await agent.assist(session, query, response_handler)
    
    # Check that events were emitted
    assert len(response_handler.events) > 0