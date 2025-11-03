#!/usr/bin/env python3
"""
Benchmark agent performance
"""
import asyncio
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.provenance_guardian import ProvenanceGuardian
from sentient_agent_framework import Session, Query
from api.routes import SSEResponseHandler


async def benchmark_command(command: str, iterations: int = 3):
    """Benchmark a command"""
    print(f"\nBenchmarking: {command}")
    print(f"Iterations: {iterations}")
    
    agent = ProvenanceGuardian()
    times = []
    
    for i in range(iterations):
        session = Session(session_id=f"bench_{i}")
        query = Query(prompt=command)
        handler = SSEResponseHandler()
        
        start = time.time()
        await agent.assist(session, query, handler)
        duration = time.time() - start
        
        times.append(duration)
        print(f"  Run {i+1}: {duration:.3f}s")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\nResults:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")
    
    return avg_time


async def main():
    """Run benchmarks"""
    print("⏱️  Provenance Guardian Performance Benchmark")
    print("="*60)
    
    commands = [
        "help",
        "verify yourself",
        "how do I fingerprint my model?",
    ]
    
    results = {}
    
    for cmd in commands:
        try:
            avg = await benchmark_command(cmd)
            results[cmd] = avg
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("Summary:")
    for cmd, avg in results.items():
        print(f"  {cmd[:40]:<40} {avg:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())