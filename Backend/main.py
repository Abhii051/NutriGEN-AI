"""
NutriGEN-AI Backend Entry Point
Exposes the FastAPI application from Backend.server for execution via:
    python Backend/main.py
    python -m uvicorn Backend.server:app --reload --port 8000
"""

from pathlib import Path
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Backend.server import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Backend.server:app", host="0.0.0.0", port=8000, reload=True)
