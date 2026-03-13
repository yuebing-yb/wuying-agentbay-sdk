"""
OpenClaw in AgentBay - Web Service Entry Point.

Start the FastAPI web server for managing OpenClaw sandbox sessions.

Usage:
    python main.py [--host HOST] [--port PORT]

Environment Variables:
    AGENTBAY_API_KEY: Optional default API key (can be overridden per request)
"""

import argparse
import logging
import os

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="OpenClaw in AgentBay - Web Service"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind the server (default: 8080)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    return parser.parse_args()


def main() -> None:
    """Start the FastAPI web server."""
    args = parse_args()

    # Check for optional default API key
    api_key = os.getenv("AGENTBAY_API_KEY")
    if api_key:
        logger.info("AGENTBAY_API_KEY environment variable is set (can be used as default)")
    else:
        logger.info("AGENTBAY_API_KEY environment variable not set (API key must be provided per request)")

    logger.info(f"Starting OpenClaw in AgentBay web service on {args.host}:{args.port}")
    logger.info("Access the web UI at http://localhost:%s", args.port)
    logger.info("API documentation available at http://localhost:%s/docs", args.port)

    # Import and run the FastAPI app
    from src.app import app

    uvicorn.run(
        "src.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
