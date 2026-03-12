"""
Real-time Code Streaming with AgentBay

This example demonstrates the streaming code execution feature (beta),
which delivers stdout/stderr output in real-time via WebSocket callbacks
instead of waiting for the entire execution to finish.

Use cases:
  - Real-time progress monitoring of long-running tasks
  - Interactive data analysis with live output
  - Building coding assistant UIs with streaming results

Prerequisites:
  - pip install wuying-agentbay-sdk
  - export AGENTBAY_API_KEY=your_api_key_here
  - A session image that supports WebSocket streaming (ws_url must be available)
"""

import os
import sys
import asyncio
import time

from agentbay import AsyncAgentBay, CreateSessionParams


async def demo_progress_monitoring(session):
    """Demonstrate real-time progress monitoring."""
    print("=" * 60)
    print("Demo 1: Real-time Progress Monitoring")
    print("=" * 60)

    chunks = []
    timestamps = []

    def on_stdout(chunk: str):
        chunks.append(chunk)
        timestamps.append(time.time())
        print(f"  [{time.time() - t0:.1f}s] {chunk}", end="", flush=True)

    def on_error(err):
        print(f"  [ERROR] {err}")

    code = """
import time

tasks = [
    ("Connecting to database", 0.5),
    ("Loading dataset (1M rows)", 0.8),
    ("Running analysis", 1.0),
    ("Generating report", 0.5),
    ("Uploading results", 0.3),
]

for i, (task, duration) in enumerate(tasks, 1):
    print(f"[{i}/{len(tasks)}] {task}...", flush=True)
    time.sleep(duration)
    print(f"  ✓ Done ({duration}s)", flush=True)

print(f"\\nAll {len(tasks)} tasks completed successfully!", flush=True)
"""

    t0 = time.time()
    result = await session.code.run_code(
        code, "python", 60,
        stream_beta=True,
        on_stdout=on_stdout,
        on_error=on_error,
    )
    total = time.time() - t0

    print(f"\n  Execution time: {total:.1f}s")
    print(f"  Chunks received: {len(chunks)}")
    print(f"  Success: {result.success}")

    if timestamps and len(timestamps) >= 2:
        first_chunk_delay = timestamps[0] - t0
        print(f"  Time to first chunk: {first_chunk_delay:.2f}s")


async def demo_streaming_analysis(session):
    """Demonstrate streaming data analysis output."""
    print("\n" + "=" * 60)
    print("Demo 2: Streaming Data Analysis")
    print("=" * 60)

    def on_stdout(chunk: str):
        print(f"  {chunk}", end="", flush=True)

    code = """
import time
import math
import random

random.seed(42)
data = [random.gauss(100, 15) for _ in range(500)]

print("=== Data Analysis Report ===", flush=True)
time.sleep(0.3)

# Basic stats
mean = sum(data) / len(data)
print(f"\\nSamples: {len(data)}", flush=True)
print(f"Mean: {mean:.2f}", flush=True)
time.sleep(0.3)

# Std deviation
variance = sum((x - mean) ** 2 for x in data) / len(data)
std = math.sqrt(variance)
print(f"Std Dev: {std:.2f}", flush=True)
time.sleep(0.3)

# Percentiles
sorted_data = sorted(data)
p25 = sorted_data[len(data) // 4]
p50 = sorted_data[len(data) // 2]
p75 = sorted_data[3 * len(data) // 4]
print(f"\\nPercentiles:", flush=True)
print(f"  25th: {p25:.2f}", flush=True)
print(f"  50th: {p50:.2f}", flush=True)
print(f"  75th: {p75:.2f}", flush=True)
time.sleep(0.3)

# Histogram
print(f"\\nDistribution:", flush=True)
bins = [0] * 10
for x in data:
    idx = min(int((x - 40) / 12), 9)
    idx = max(0, idx)
    bins[idx] += 1
for i, count in enumerate(bins):
    low = 40 + i * 12
    bar = "█" * (count // 5)
    print(f"  {low:6.0f}-{low+12:6.0f}: {bar} ({count})", flush=True)
    time.sleep(0.1)

print(f"\\n=== Report Complete ===", flush=True)
"""

    t0 = time.time()
    result = await session.code.run_code(
        code, "python", 60,
        stream_beta=True,
        on_stdout=on_stdout,
    )
    print(f"\n  Total time: {time.time() - t0:.1f}s, Success: {result.success}")


async def demo_comparison(session):
    """Compare streaming vs non-streaming execution."""
    print("\n" + "=" * 60)
    print("Demo 3: Streaming vs Non-Streaming Comparison")
    print("=" * 60)

    code = """
import time
for i in range(5):
    print(f"Step {i+1}/5: Processing...", flush=True)
    time.sleep(0.5)
print("Complete!", flush=True)
"""

    # Non-streaming
    print("\n  [Non-Streaming] Waiting for all output...")
    t0 = time.time()
    r1 = await session.code.run_code(code, "python", 30)
    t_non_stream = time.time() - t0
    print(f"  Received all output at once after {t_non_stream:.1f}s:")
    for line in "\n".join(r1.logs.stdout).strip().split("\n"):
        print(f"    {line}")

    # Streaming
    first_chunk_time = None

    def on_stdout(chunk: str):
        nonlocal first_chunk_time
        if first_chunk_time is None:
            first_chunk_time = time.time()
        print(f"    [{time.time() - t0:.1f}s] {chunk}", end="", flush=True)

    print(f"\n  [Streaming] Real-time output:")
    t0 = time.time()
    r2 = await session.code.run_code(
        code, "python", 30,
        stream_beta=True,
        on_stdout=on_stdout,
    )
    t_stream = time.time() - t0

    print(f"\n  Non-streaming: output delivered at {t_non_stream:.1f}s")
    if first_chunk_time:
        print(f"  Streaming: first chunk at {first_chunk_time - t0:.1f}s (total {t_stream:.1f}s)")
        print(f"  First-output latency improvement: {t_non_stream - (first_chunk_time - t0):.1f}s earlier")


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: Please set the AGENTBAY_API_KEY environment variable")
        sys.exit(1)

    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None

    try:
        print("Creating session...")
        result = await agent_bay.create(CreateSessionParams())
        if not result.success:
            print(f"Failed: {result.error_message}")
            return
        session = result.session
        print(f"Session: {session.session_id}")

        if not session.ws_url:
            print("Error: This session does not support WebSocket streaming (ws_url is empty).")
            print("Please use an image that supports ws_url.")
            return

        print(f"WebSocket URL available: {session.ws_url[:60]}...\n")

        await demo_progress_monitoring(session)
        await demo_streaming_analysis(session)
        await demo_comparison(session)

        print("\n" + "=" * 60)
        print("All demos completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if session:
            print("\nCleaning up session...")
            await session.delete()
            print("Session deleted.")


if __name__ == "__main__":
    asyncio.run(main())
