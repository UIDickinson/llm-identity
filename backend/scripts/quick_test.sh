#!/bin/bash
# Quick test script to verify agent is working

echo "🧪 Quick Agent Test"
echo "=================="

# Activate virtual environment if exists
if [ -d "env" ]; then
    source env/bin/activate
fi

# Run quick test
python3 << 'EOF'
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from agent.provenance_guardian import ProvenanceGuardian
from sentient_agent_framework import Session, Query
from api.routes import SSEResponseHandler

async def test():
    print("\n1. Testing agent initialization...")
    agent = ProvenanceGuardian()
    print("   ✅ Agent initialized")
    
    print("\n2. Testing help command...")
    session = Session(session_id="test")
    query = Query(prompt="help")
    handler = SSEResponseHandler()
    
    await agent.assist(session, query, handler)
    
    if len(handler.events) > 0:
        print("   ✅ Help command works")
    else:
        print("   ❌ No events received")
        return False
    
    print("\n3. Testing self-verification...")
    query = Query(prompt="verify yourself")
    handler = SSEResponseHandler()
    
    await agent.assist(session, query, handler)
    
    if len(handler.events) > 0:
        print("   ✅ Self-verification command works")
    else:
        print("   ❌ No events received")
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test())
    
    if result:
        print("\n✅ All quick tests passed!")
        print("\nAgent is ready to use.")
        print("\nNext steps:")
        print("  • Run: uvicorn api.server:app --reload")
        print("  • Open: http://localhost:8000")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
EOF