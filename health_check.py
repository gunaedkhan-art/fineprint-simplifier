#!/usr/bin/env python3
"""
Minimal health check module with no external dependencies
"""

import time

def get_health_status():
    """Get basic health status"""
    try:
        return {
            "status": "healthy",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "version": "1.0.0",
            "app": "Fineprint Simplifier"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "unknown"
        }
