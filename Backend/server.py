"""
NutriGEN-AI: Layer 3 REST API Server (FastAPI)
Exposes endpoints for nutritional calculation, meal plan optimization, and LLM recipe generation.
Includes CORS support and serves the modern frontend application.
"""

import os
from pathlib import Path
import sys
from typing import List, Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Backend.src.pipeline import run_nutrigen_pipeline
from ai_model import generate_nutrition_profile


app = FastAPI(
    title="NutriGEN-AI API",
    description="Personalized Nutrition & Diet Optimization with AI Chef Recipe Generation",
    version="1.0.0"
)

# CORS configuration (Configurable via ALLOWED_ORIGINS environment variable)
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# PYDANTIC SCHEMAS
# =====================================================================

class PlanGenerationRequest(BaseModel):
    age: int = Field(22, ge=1, le=120, description="Age in years")
    sex: Literal["male", "female"] = Field("male", description="Biological sex")
    height_cm: float = Field(175.0, ge=50.0, le=250.0, description="Height in centimeters")
    weight_kg: float = Field(70.0, ge=20.0, le=300.0, description="Weight in kilograms")
    target_weight_kg: Optional[float] = Field(None, ge=20.0, le=300.0, description="Target goal weight in kilograms")
    activity_level: str = Field(
        "moderate",
        description="sedentary, light, moderate, very_active, extremely_active"
    )
    goal: str = Field(
        "maintenance",
        description="weight_loss, maintenance, weight_gain"
    )
    diet_type: str = Field(
        "vegetarian",
        description="vegetarian, vegan, non-vegetarian"
    )
    allergies: List[str] = Field(
        default_factory=list,
        description="List of allergen keywords to filter out (e.g. ['peanuts', 'milk'])"
    )
    disliked_foods: List[str] = Field(
        default_factory=list,
        description="List of ingredients the user dislikes (e.g. ['mushroom'])"
    )
    cuisine: str = Field(
        "indian",
        description="Cuisine preference (e.g. indian, mediterranean)"
    )
    eats_eggs: bool = Field(
        False,
        description="Whether the user consumes eggs (vegetarian only)"
    )
    number_of_meals: int = Field(
        3,
        ge=3,
        le=5,
        description="Number of main meals per day"
    )
    number_of_snacks: int = Field(
        1,
        ge=0,
        le=2,
        description="Number of snacks per day"
    )
    user_prompt: Optional[str] = Field(
        "",
        description="Custom cooking instructions for the AI Chef (e.g. '15 mins to cook, spicy, no oven')"
    )
    groq_api_key: Optional[str] = Field(
        None,
        description="Optional Groq API Key for Meta Llama 3.1 8B recipe generation"
    )


# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.get("/api/health")
def health_check():
    """Health check endpoint to verify API status."""
    return {
        "status": "healthy",
        "service": "NutriGEN-AI Backend API",
        "version": "1.0.0"
    }


@app.post("/api/generate-plan")
def generate_plan_endpoint(request: PlanGenerationRequest):
    """
    Main endpoint for generating personalized nutrition targets, optimized meal plan,
    and chef-crafted recipes.
    """
    try:
        user_data = request.model_dump()
        result = run_nutrigen_pipeline(user_data)
        return result

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Required food dataset was not found on server."
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the meal plan: {str(exc)}"
        ) from exc


# Aliases for backwards compatibility
@app.post("/api/meal-plan/generate")
def generate_meal_plan_alias(request: PlanGenerationRequest):
    return generate_plan_endpoint(request)


@app.post("/generate-meal-plan")
def generate_meal_plan_root_alias(request: PlanGenerationRequest):
    """Root-level alias used by earlier frontend script versions."""
    return generate_plan_endpoint(request)


@app.post("/api/nutrition/requirements")
def nutrition_requirements_endpoint(request: PlanGenerationRequest):
    """Returns biological energy and macronutrient requirements only."""
    try:
        profile = generate_nutrition_profile(
            age=request.age,
            weight_kg=request.weight_kg,
            height_cm=request.height_cm,
            sex=request.sex,
            activity_level=request.activity_level.lower(),
            goal=request.goal.lower()
        )
        return {
            "status": "success",
            "nutrition_requirements": {
                "bmr": profile["bmr"],
                "tdee": profile["tdee"],
                "calories": profile["calorie_target"],
                "protein_g": profile["protein_g"],
                "fat_g": profile["fat_g"],
                "carbs_g": profile["carbs_g"]
            }
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# =====================================================================
# FRONTEND STATIC FILES & SPA SERVING
# =====================================================================

FRONTEND_DIR = PROJECT_ROOT / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = PROJECT_ROOT / "Frontend"

if FRONTEND_DIR.exists():
    # Mount static files at root so /index.html, /style.css, /script.js are all served
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Backend.server:app", host="0.0.0.0", port=8000, reload=True)
