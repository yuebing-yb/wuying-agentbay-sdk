"""
Multi-Session Orchestration with AgentBay

This example demonstrates how to run multiple tasks concurrently using
separate cloud sessions, achieving significant speedup over sequential execution.

Workflow:
  1. Define independent computational tasks
  2. Run them sequentially and measure time
  3. Run them concurrently and measure time
  4. Compare results and show speedup

Prerequisites:
  - pip install wuying-agentbay-sdk
  - export AGENTBAY_API_KEY=your_api_key_here
"""

import os
import sys
import asyncio
import time
import json

from agentbay import AsyncAgentBay, CreateSessionParams


async def run_task(agent_bay, task_name: str, code: str, language: str = "python"):
    """Create a session, run code, and return the result."""
    t_start = time.time()

    result = await agent_bay.create(CreateSessionParams(image_id="code_latest"))
    if not result.success:
        return {
            "task": task_name,
            "success": False,
            "error": result.error_message,
        }
    session = result.session
    create_time = time.time() - t_start

    try:
        t_exec = time.time()
        r = await session.code.run_code(code, language, 30)
        exec_time = time.time() - t_exec
        total_time = time.time() - t_start

        output = "\n".join(r.logs.stdout) if r.logs.stdout else ""

        return {
            "task": task_name,
            "success": r.success,
            "output": output.strip(),
            "create_time": create_time,
            "exec_time": exec_time,
            "total_time": total_time,
            "session_id": session.session_id,
        }
    finally:
        await session.delete()


# Define tasks
TASKS = [
    (
        "Prime Numbers",
        """
def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(n+1) if is_prime[i]]

primes = sieve(10000)
print(f"Primes up to 10000: {len(primes)} found")
print(f"First 10: {primes[:10]}")
print(f"Last 10: {primes[-10:]}")
""",
    ),
    (
        "System Info",
        """
import platform, os, json

info = {
    "python": platform.python_version(),
    "os": f"{platform.system()} {platform.release()}",
    "arch": platform.machine(),
    "cpu_count": os.cpu_count(),
    "cwd": os.getcwd(),
}
print(json.dumps(info, indent=2))
""",
    ),
    (
        "Statistics",
        """
import math, random

random.seed(42)
data = [random.gauss(100, 15) for _ in range(1000)]

mean = sum(data) / len(data)
variance = sum((x - mean) ** 2 for x in data) / len(data)
std_dev = math.sqrt(variance)
sorted_data = sorted(data)
median = sorted_data[len(data) // 2]

print(f"Samples: {len(data)}")
print(f"Mean: {mean:.2f}")
print(f"Std Dev: {std_dev:.2f}")
print(f"Median: {median:.2f}")
print(f"Min: {min(data):.2f}")
print(f"Max: {max(data):.2f}")
""",
    ),
]


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: Please set the AGENTBAY_API_KEY environment variable")
        sys.exit(1)

    agent_bay = AsyncAgentBay(api_key=api_key)

    # --- Sequential Execution ---
    print("=" * 60)
    print("Sequential Execution")
    print("=" * 60)

    t_seq_start = time.time()
    seq_results = []
    for name, code in TASKS:
        print(f"\n  Running '{name}'...")
        r = await run_task(agent_bay, name, code)
        seq_results.append(r)
        if r["success"]:
            print(f"    Create: {r['create_time']:.1f}s | Exec: {r['exec_time']:.1f}s | Total: {r['total_time']:.1f}s")
        else:
            print(f"    Failed: {r.get('error', 'unknown')}")
    seq_total = time.time() - t_seq_start

    # --- Concurrent Execution ---
    print("\n" + "=" * 60)
    print("Concurrent Execution")
    print("=" * 60)

    t_conc_start = time.time()
    conc_tasks = [run_task(agent_bay, name, code) for name, code in TASKS]
    conc_results = await asyncio.gather(*conc_tasks, return_exceptions=True)
    conc_total = time.time() - t_conc_start

    for r in conc_results:
        if isinstance(r, Exception):
            print(f"\n  Error: {r}")
        elif r["success"]:
            print(f"\n  '{r['task']}':")
            print(f"    Create: {r['create_time']:.1f}s | Exec: {r['exec_time']:.1f}s | Total: {r['total_time']:.1f}s")
            for line in r["output"].split("\n")[:3]:
                print(f"    > {line}")
        else:
            print(f"\n  '{r['task']}': Failed - {r.get('error', 'unknown')}")

    # --- Comparison ---
    print("\n" + "=" * 60)
    print("Results Comparison")
    print("=" * 60)

    seq_success = sum(1 for r in seq_results if r["success"])
    conc_success = sum(1 for r in conc_results
                       if not isinstance(r, Exception) and r["success"])

    print(f"\n  Sequential:  {seq_total:.1f}s ({seq_success}/{len(TASKS)} succeeded)")
    print(f"  Concurrent:  {conc_total:.1f}s ({conc_success}/{len(TASKS)} succeeded)")
    print(f"  Speedup:     {seq_total / conc_total:.1f}x")
    print(f"  Time saved:  {seq_total - conc_total:.1f}s")

    # Output results as JSON
    print("\n  Detailed results (concurrent):")
    for r in conc_results:
        if isinstance(r, Exception):
            continue
        if r["success"]:
            print(f"\n  [{r['task']}]")
            print(f"  {r['output']}")


if __name__ == "__main__":
    asyncio.run(main())
