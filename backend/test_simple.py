import asyncio
import sys
import uuid
from pathlib import Path
from ulid import ULID

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.provenance_guardian import ProvenanceGuardian
from sentient_agent_framework.interface.request import Query
from sentient_agent_framework.interface.session import SessionObject

class SimpleEventHandler:
    """Simple handler that implements the response handler interface"""
    def __init__(self):
        self.events = []
    
    async def emit_text_block(self, content: str, *args, **kwargs):
        """Handle text block events"""
        self.events.append({"type": "TEXT_BLOCK", "content": content})
        print(f"   📝 Text: {content[:100]}...")
    
    async def emit_json(self, data: dict, event_type: str = None, *args, **kwargs):
        """Handle JSON events"""
        self.events.append({"type": "JSON", "data": data, "event_type": event_type})
        print(f"   📊 JSON Event: {event_type}")
    
    async def emit_done(self, *args, **kwargs):
        """Handle completion"""
        self.events.append({"type": "DONE"})
        print(f"   ✅ Done")
    
    async def emit_error(self, error: str, *args, **kwargs):
        """Handle errors"""
        self.events.append({"type": "ERROR", "error": error})
        print(f"   ❌ Error: {error}")
    
    async def complete(self, *args, **kwargs):
        """Mark handler as complete"""
        pass

async def test():
    print("🧪 Testing Provenance Guardian\n")
    
    print("1. Initializing agent...")
    agent = ProvenanceGuardian()
    print("   ✅ Agent initialized\n")
    
    # Create proper SessionObject with all required fields
    session = SessionObject(
        session_id="test-session",
        processor_id=str(uuid.uuid4()),
        activity_id=str(ULID()),
        request_id=str(ULID()),
        interactions=[]
    )
    print(f"   ✅ Session created\n")
    
    # Test 1: Help command
    print("2. Testing help command...")
    handler = SimpleEventHandler()
    query1 = Query(id=str(ULID()), prompt="help")
    await agent.assist(session, query1, handler)
    print(f"   ✅ Got {len(handler.events)} events\n")
    
    # Test 2: Self-verification
    print("3. Testing self-verification...")
    handler = SimpleEventHandler()
    query2 = Query(id=str(ULID()), prompt="verify yourself")
    await agent.assist(session, query2, handler)
    print(f"   ✅ Got {len(handler.events)} events\n")
    
    # Test 3: Fingerprint guide
    print("4. Testing fingerprint guide...")
    handler = SimpleEventHandler()
    query3 = Query(id=str(ULID()), prompt="how do I fingerprint my model?")
    await agent.assist(session, query3, handler)
    print(f"   ✅ Got {len(handler.events)} events\n")
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test())