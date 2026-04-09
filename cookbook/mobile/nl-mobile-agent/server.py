#!/usr/bin/env python3
"""
NL Mobile Agent Web Demo (FastAPI + SSE).

Uses AgentBay's built-in mobile agent (session.agent.mobile) to execute
natural language tasks on a cloud phone. Agent events are streamed to
the browser via Server-Sent Events (SSE).

Only requires: AGENTBAY_API_KEY
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from agentbay import AsyncAgentBay, AgentEvent, CreateSessionParams


DEFAULT_IMAGE_ID = "mobile_latest"


def _web_index() -> str:
    html_path = Path(__file__).resolve().parent / "web" / "index.html"
    return html_path.read_text(encoding="utf-8")


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise HTTPException(status_code=400, detail=f"Missing env var: {name}")
    return v


@dataclass
class SessionState:
    session_id: str
    resource_url: str
    image_id: str
    created_at_s: float = field(default_factory=lambda: time.time())


@dataclass
class JobState:
    job_id: str
    status: str
    prompt: str
    events: List[Dict[str, Any]] = field(default_factory=list)
    final_answer: str = ""
    error: str = ""
    started_at_s: float = field(default_factory=lambda: time.time())
    finished_at_s: float = 0.0
    waiters: List[asyncio.Queue] = field(default_factory=list)


app = FastAPI()

_lock = asyncio.Lock()
_session: Optional[SessionState] = None
_agentbay_session: Any = None
_client: Optional[AsyncAgentBay] = None
_jobs: Dict[str, JobState] = {}


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return _web_index()


@app.get("/api/session")
async def get_session() -> Dict[str, Any]:
    if _session is None:
        return {"session_id": "", "resource_url": "", "image_id": ""}
    return {
        "session_id": _session.session_id,
        "resource_url": _session.resource_url,
        "image_id": _session.image_id,
        "created_at_s": _session.created_at_s,
    }


@app.post("/api/session/create")
async def create_session(_: Dict[str, Any]) -> Dict[str, Any]:
    _require_env("AGENTBAY_API_KEY")

    async with _lock:
        global _session, _agentbay_session, _client
        if _session is not None:
            return {
                "session_id": _session.session_id,
                "resource_url": _session.resource_url,
                "image_id": _session.image_id,
                "mode": "existing",
            }

        image_id = os.getenv("MOBILE_IMAGE_ID", DEFAULT_IMAGE_ID)
        _client = AsyncAgentBay(api_key=os.environ["AGENTBAY_API_KEY"])
        res = await _client.create(CreateSessionParams(image_id=image_id))
        if not res.success or not res.session:
            raise HTTPException(
                status_code=500,
                detail=res.error_message or "create_session_failed",
            )

        s = res.session
        _agentbay_session = s
        _session = SessionState(
            session_id=s.session_id,
            resource_url=getattr(s, "resource_url", "") or "",
            image_id=image_id,
        )
        return {
            "session_id": _session.session_id,
            "resource_url": _session.resource_url,
            "image_id": _session.image_id,
            "mode": "created",
        }


@app.post("/api/session/delete")
async def delete_session(_: Dict[str, Any]) -> Dict[str, Any]:
    _require_env("AGENTBAY_API_KEY")
    async with _lock:
        global _session, _agentbay_session, _client
        if _session is None:
            return {"success": True, "deleted": False}
        if _client and _agentbay_session:
            await _client.delete(_agentbay_session)
        _session = None
        _agentbay_session = None
        _client = None
        return {"success": True, "deleted": True}


def _sse_event(event_type: str, data: Any) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {payload}\n\n"


@app.post("/api/agent/run")
async def run_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    _require_env("AGENTBAY_API_KEY")

    async with _lock:
        if _session is None or _agentbay_session is None:
            raise HTTPException(status_code=400, detail="session not created")
        job_id = uuid.uuid4().hex[:12]
        job = JobState(job_id=job_id, status="running", prompt=prompt)
        _jobs[job_id] = job
        asyncio.create_task(_run_job(job_id))
        return {"job_id": job_id}


@app.get("/api/agent/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    """SSE endpoint: streams agent events in real time."""
    from starlette.responses import StreamingResponse

    j = _jobs.get(job_id)
    if not j:
        raise HTTPException(status_code=404, detail="job not found")

    queue: asyncio.Queue = asyncio.Queue()
    j.waiters.append(queue)

    async def event_generator():
        for past in j.events:
            yield _sse_event(past.get("type", "log"), past)

        if j.status in ("succeeded", "failed"):
            yield _sse_event("done", {"status": j.status, "final_answer": j.final_answer, "error": j.error})
            return

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=300)
            except asyncio.TimeoutError:
                yield _sse_event("heartbeat", {})
                continue

            if event is None:
                break
            yield _sse_event(event.get("type", "log"), event)
            if event.get("type") == "done":
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/agent/jobs/{job_id}")
async def get_job(job_id: str) -> Dict[str, Any]:
    j = _jobs.get(job_id)
    if not j:
        raise HTTPException(status_code=404, detail="job not found")
    return {
        "job_id": j.job_id,
        "status": j.status,
        "prompt": j.prompt,
        "events": j.events,
        "final_answer": j.final_answer,
        "error": j.error,
        "started_at_s": j.started_at_s,
        "finished_at_s": j.finished_at_s,
    }


def _broadcast(job: JobState, event: Dict[str, Any]) -> None:
    job.events.append(event)
    for q in job.waiters:
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            pass


def _finish_broadcast(job: JobState) -> None:
    for q in job.waiters:
        try:
            q.put_nowait(None)
        except asyncio.QueueFull:
            pass
    job.waiters.clear()


async def _run_job(job_id: str) -> None:
    j = _jobs[job_id]

    async with _lock:
        if _agentbay_session is None:
            j.status = "failed"
            j.error = "session not created"
            j.finished_at_s = time.time()
            _broadcast(j, {"type": "done", "status": "failed", "error": j.error})
            _finish_broadcast(j)
            return
        session = _agentbay_session

    _broadcast(j, {"type": "log", "message": f"Starting task on session {_session.session_id}..."})

    def on_reasoning(event: AgentEvent):
        _broadcast(j, {"type": "reasoning", "content": event.content or ""})

    def on_content(event: AgentEvent):
        _broadcast(j, {"type": "content", "content": event.content or ""})

    def on_tool_call(event: AgentEvent):
        args_str = json.dumps(event.args, ensure_ascii=False) if event.args else ""
        _broadcast(j, {
            "type": "tool_call",
            "tool_name": event.tool_name or "",
            "args": args_str,
        })

    def on_tool_result(event: AgentEvent):
        result_str = str(event.result)[:500] if event.result else ""
        _broadcast(j, {
            "type": "tool_result",
            "tool_name": event.tool_name or "",
            "result": result_str,
        })

    def on_error(event: AgentEvent):
        _broadcast(j, {"type": "error", "error": str(event.error or "")})

    try:
        max_steps = int(os.getenv("MOBILE_MAX_STEPS", "50"))
        timeout = int(os.getenv("MOBILE_TIMEOUT", "180"))

        result = await session.agent.mobile.execute_task_and_wait(
            task=j.prompt,
            timeout=timeout,
            max_steps=max_steps,
            on_reasoning=on_reasoning,
            on_content=on_content,
            on_tool_call=on_tool_call,
            on_tool_result=on_tool_result,
            on_error=on_error,
        )

        j.final_answer = result.task_result or ""
        if result.success:
            j.status = "succeeded"
        else:
            j.status = "failed"
            j.error = result.error_message or "task_failed"
    except Exception as e:
        j.status = "failed"
        j.error = str(e)
    finally:
        j.finished_at_s = time.time()
        _broadcast(j, {
            "type": "done",
            "status": j.status,
            "final_answer": j.final_answer,
            "error": j.error,
        })
        _finish_broadcast(j)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
