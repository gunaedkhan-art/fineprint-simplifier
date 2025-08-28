#!/usr/bin/env python3
import os
import uvicorn
import sys

def main():
    # Try multiple port options
    port_options = [
        os.environ.get("PORT"),  # Railway's PORT
        os.environ.get("RAILWAY_STATIC_URL"),  # Alternative Railway port
        8000,  # Default fallback
        8080,  # Common Railway port
        3000,  # Another common port
    ]
    
    port = None
    for option in port_options:
        if option:
            try:
                port = int(option)
                print(f"Using port: {port}")
                break
            except (ValueError, TypeError):
                continue
    
    if not port:
        port = 8000
        print(f"No valid port found, using default: {port}")
    
    print(f"Starting server on port {port}")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
