"""
FastAPI application for OpenClaw session management.

Provides REST API endpoints for creating, querying, and deleting OpenClaw sandbox sessions.
Serves the frontend static files.
"""

import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .models import CreateSessionRequest, SessionResponse
from .session_manager import session_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenClaw in AgentBay",
    description="REST API for managing OpenClaw sandbox sessions",
    version="1.0.0",
)

# CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory (parent of src = python/, static is in python/)
STATIC_DIR = Path(__file__).parent.parent / "static"


# ── API Routes ─────────────────────────────────────────────────────


@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new OpenClaw sandbox session.

    Flow: Create sandbox -> Write config -> Start Gateway -> Open Dashboard -> Return resource_url
    """
    # Validate required fields
    if not request.agentbay_api_key or not request.agentbay_api_key.strip():
        raise HTTPException(status_code=400, detail="agentbayApiKey cannot be empty")
    if not request.bailian_api_key or not request.bailian_api_key.strip():
        raise HTTPException(status_code=400, detail="bailianApiKey cannot be empty")
    if not request.username or not request.username.strip():
        raise HTTPException(status_code=400, detail="username cannot be empty")

    try:
        response = session_manager.create_session(request)
        return response
    except Exception as e:
        logger.error(f"Failed to create session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Query session status by ID."""
    response = session_manager.get_session(session_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return response


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Destroy a session by ID."""
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session destroyed", "sessionId": session_id}


@app.get("/api/sessions", response_model=List[SessionResponse])
async def list_sessions():
    """List all active sessions."""
    return session_manager.list_sessions()


# ── Static Files ───────────────────────────────────────────────────


@app.get("/")
async def serve_index():
    """Serve the frontend index.html."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/assets/{file_path:path}")
async def serve_assets(file_path: str):
    """Serve frontend static assets."""
    asset_path = STATIC_DIR / "assets" / file_path
    if asset_path.exists():
        return FileResponse(asset_path)
    raise HTTPException(status_code=404, detail="Asset not found")


# ── Error Handlers ──────────────────────────────────────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler to ensure consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
