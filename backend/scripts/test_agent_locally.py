#!/usr/bin/env python3
"""
Test the agent locally without running the full server
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.provenance_guardian import ProvenanceGuardian
from sentient_agent_framework import Session, Query
from api.routes import SSEResponseHandler


async def test_command(command: str):
    """Test a single command"""
    print(f"\n{'='*60}")
    print(f"Testing: {command}")
    print('='*60)
    
    agent = ProvenanceGuardian()
    session = Session(session_id="test")
    query = Query(prompt=command)
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
    
    # Test commands
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
        
        # Wait between commands
        await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print("✅ Test suite complete!")


if __name__ == "__main__":
    asyncio.run(main())