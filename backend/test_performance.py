"""
Performance benchmarking
"""
import asyncio
import time
import sys
import uuid
from ulid import ULID

from sentient_agent_framework.interface.session import SessionObject
from sentient_agent_framework.interface.request import Query
from agent.provenance_guardian import ProvenanceGuardian
from api.routes import SSEResponseHandler


async def benchmark_command(agent, command: str, iterations: int = 3):
    """Benchmark a command"""
    print(f"\n📊 Benchmarking: {command}")
    times = []
    
    for i in range(iterations):
        session = SessionObject(
            session_id=f"bench-{i}",
            processor_id=str(uuid.uuid4()),
            activity_id=str(ULID()),
            request_id=str(ULID()),
            interactions=[]
        )
        query = Query(id=str(ULID()), prompt=command)
        handler = SSEResponseHandler()
        
        start = time.time()
        await agent.assist(session, query, handler)
        duration = time.time() - start
        
        times.append(duration)
        print(f"  Run {i+1}: {duration:.3f}s")
    
    avg = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"  Average: {avg:.3f}s | Min: {min_time:.3f}s | Max: {max_time:.3f}s")
    return avg


async def main():
    print("⏱️  PERFORMANCE BENCHMARKS")
    print("="*60)
    
    agent = ProvenanceGuardian()
    
    commands = [
        "help",
        "verify yourself",
        "how do I fingerprint my model?",
        "generate fingerprints for me",
    ]
    
    results = {}
    for cmd in commands:
        results[cmd] = await benchmark_command(agent, cmd)
        await asyncio.sleep(0.5)
    
    print("\n" + "="*60)
    print("📈 SUMMARY")
    print("="*60)
    for cmd, avg_time in results.items():
        print(f"{cmd[:40]:<40} {avg_time:.3f}s")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())