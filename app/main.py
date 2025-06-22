"""
Main application entry point.
Starts the ASGI server with configured host and port settings.
"""
from typing import Final

import uvicorn

from app.startup import app

# Server configuration constants
HOST: Final[str] = "0.0.0.0"
PORT: Final[int] = 8000

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=HOST,
        port=PORT
    )
