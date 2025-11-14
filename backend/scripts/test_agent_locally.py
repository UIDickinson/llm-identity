#!/usr/bin/env python3
"""
Test the agent locally without running the full server
"""
import asyncio
import sys
import uuid
from pathlib import Path
from ulid import ULID
from sentient_agent_framework.interface.session import SessionObject
from sentient_agent_framework.interface.request import Query
from agent.provenance_guardian import ProvenanceGuardian
from api.routes import SSEResponseHandler


async def test_command(cmd: str):
    """Test a single command"""
    print(f"\n{'='*60}")
    print(f"Testing: {cmd}")
    print('='*60)
    
    agent = ProvenanceGuardian()
    session = SessionObject(
        session_id="test",
        processor_id=str(uuid.uuid4()),
        activity_id=str(ULID()),
        request_id=str(ULID()),
        interactions=[]
    )
    query = Query(id=str(ULID()), prompt=cmd)
    handler = SSEResponseHandler()
    
    await agent.assist(session, query, handler)
    
    # Print events
    print("\nEvents received:")
    for i, event in enumerate(handler.events):
        print(f"\n[Event {i+1}]")
        if event['type'] == 'text_block':
            print(f"Type: TEXT_BLOCK")
            print(f"Content: {event['content'][:200]}...")
        elif event['type'] == 'json':
            print(f"Type: JSON")
            print(f"Event Type: {event.get('event_type')}")
        elif event['type'] == 'done':
            print("Type: DONE")


async def main():
    """Run test suite"""
    
    print("🧪 Provenance Guardian Local Test Suite")
    print("="*60)
    
    commands = [
        "help",
        "verify yourself",
        "how do I fingerprint my model?",
        "generate fingerprints for me",
    ]
    
    for cmd in commands:
        try:
            await test_command(cmd)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print("✅ Test suite complete!")


if __name__ == "__main__":
    asyncio.run(main())