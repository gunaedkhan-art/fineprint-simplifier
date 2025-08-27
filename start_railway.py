#!/usr/bin/env python3
import os
import sys
import uvicorn

def main():
    # Get port from environment variable, default to 8000
    port_str = os.environ.get("PORT", "8000")
    
    try:
        port = int(port_str)
    except ValueError:
        print(f"Error: Invalid PORT value '{port_str}'. Using default port 8000.")
        port = 8000
    
    print(f"Starting server on port {port}")
    
    # Start the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
