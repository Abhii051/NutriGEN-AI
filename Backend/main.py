"""
NutriGEN-AI Backend Entry Point
Exposes the FastAPI application from Backend.server for execution via:
    uvicorn Backend.main:app --reload --port 8000
    uvicorn Backend.server:app --reload --port 8000
"""

from Backend.server import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Backend.server:app", host="0.0.0.0", port=8000, reload=True)
