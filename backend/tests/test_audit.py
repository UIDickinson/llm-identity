import pytest
from agent.audit_engine import AuditEngine


@pytest.mark.asyncio
async def test_audit_engine_initialization():
    """Test audit engine initializes"""
    engine = AuditEngine()
    assert engine.model_loader is not None
    assert engine.validator is not None


@pytest.mark.asyncio
async def test_fuzzy_match():
    """Test fuzzy matching logic"""
    engine = AuditEngine()
    
    # Exact match
    assert engine._fuzzy_match("hello world", "hello world") == True
    
    # Partial match (should pass with default threshold)
    assert engine._fuzzy_match("hello world foo", "hello world bar") == True
    
    # No match
    assert engine._fuzzy_match("completely different", "nothing similar") == False