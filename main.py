# Minimal FastAPI app for testing deployment
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2025-08-27T00:00:00",
        "version": "1.0.0",
        "app": "Fineprint Simplifier"
    }

@app.get("/")
async def root():
    return {"message": "Fineprint Simplifier is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
