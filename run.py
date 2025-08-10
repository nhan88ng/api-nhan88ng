#!/usr/bin/env python3
"""
Run the FastAPI application with uvicorn
Usage: python run.py
"""

import uvicorn
import os

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "True").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info")
    )
