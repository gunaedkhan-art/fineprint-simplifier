# Minimal FastAPI app for testing deployment
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from datetime import datetime

# Test custom module import
try:
    from core_patterns import RISK_PATTERNS, GOOD_PATTERNS
    print("✓ core_patterns imported successfully")
except Exception as e:
    print(f"✗ core_patterns import failed: {e}")
    RISK_PATTERNS = {}
    GOOD_PATTERNS = {}

app = FastAPI()

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templating
templates = Jinja2Templates(directory="templates")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "app": "Fineprint Simplifier"
    }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/test")
async def test():
    return {
        "message": "Fineprint Simplifier is running with core_patterns!",
        "risk_patterns_count": len(RISK_PATTERNS),
        "good_patterns_count": len(GOOD_PATTERNS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
