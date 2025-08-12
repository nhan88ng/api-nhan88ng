#!/usr/bin/env python3
"""
Run the FastAPI application with uvicorn
Usage: python run.py
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env_bool(key: str, default: bool = False) -> bool:
    """Convert environment variable to boolean"""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")

def main():
    """Main function to run the FastAPI application"""
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = get_env_bool("DEBUG", True)
    log_level = os.getenv("LOG_LEVEL", "info")
    
    # Production optimizations
    reload = debug  # Only reload in debug mode
    workers = 1 if debug else int(os.getenv("WORKERS", "1"))
    
    print(f"🚀 Starting Nhan88ng API server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📊 Log Level: {log_level}")
    print(f"👥 Workers: {workers}")
    print(f"🔄 Reload: {reload}")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            workers=workers if not reload else 1,  # Workers only in production
            access_log=True,
            use_colors=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()
