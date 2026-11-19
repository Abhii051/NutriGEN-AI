"""
NutriGEN-AI: Layer 3 REST API Server (FastAPI)
Exposes endpoints for nutritional calculation, meal plan optimization, and LLM recipe generation.
Includes CORS support and serves the modern frontend application.
"""

import os
import logging
from pathlib import Path
import sys
from typing import List, Optional, Literal, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Backend.src.pipeline import (
    run_nutrigen_pipeline,
    run_swap_item_pipeline,
    run_swap_meal_pipeline
)
from Backend.src.optimizer import get_alternative_foods_for_item
from ai_model import generate_nutrition_profile


app = FastAPI(
    title="NutriGEN-AI API",
    description="Personalized Nutrition & Diet Optimization with AI Chef Recipe Generation",
    version="1.0.0"
)

# CORS configuration: Defaults to explicit localhost origins for security.
# In production, set ALLOWED_ORIGINS environment variable (e.g. "https://nutrigen-ai.com,https://app.nutrigen.ai").
default_origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allowed_origins = default_origins

is_wildcard = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=not is_wildcard,  # W3C CORS Spec: credentials must be False when origin is '*'
    allow_methods=["GET", "POST", "OPTIONS"],
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
        ge=2,
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
    exclude_fdc_ids: List[int] = Field(
        default_factory=list,
        description="List of USDA FDC IDs to exclude when generating alternative plans"
    )
    variation_seed: int = Field(
        0,
        description="Seed or rotation index for generating alternative diverse plans"
    )
    plan_days: int = Field(
        1,
        ge=1,
        le=7,
        description="Number of consecutive days to generate in a multi-day plan (1 to 7)"
    )


class AlternativeFoodsRequest(BaseModel):
    fdc_id: int = Field(..., description="USDA FDC ID of the food item to find alternatives for")
    diet_type: str = Field("vegetarian", description="Diet preference (vegetarian, vegan, non-vegetarian)")
    cuisine: str = Field("indian", description="Cuisine preference")
    allergies: List[str] = Field(default_factory=list, description="Allergies to filter out")
    disliked_foods: List[str] = Field(default_factory=list, description="Disliked foods to filter out")
    eats_eggs: bool = Field(False, description="Whether eggs are allowed")
    limit: int = Field(8, ge=1, le=20, description="Max number of alternatives to return")


class SwapItemRequest(BaseModel):
    user_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User biometric and preference parameters")
    current_plan: Dict[str, Any] = Field(..., description="The current active meal plan dictionary")
    fdc_id_to_replace: int = Field(..., description="FDC ID of the food item being replaced")
    replacement_fdc_id: Optional[int] = Field(None, description="Optional chosen replacement FDC ID")
    targets: Optional[Dict[str, float]] = Field(None, description="Target calories and macros")
    cuisine: Optional[str] = Field("indian", description="Cuisine preference")
    diet_type: Optional[str] = Field("vegetarian", description="Diet preference")
    user_prompt: Optional[str] = Field("", description="Chef prompt")


class SwapMealRequest(BaseModel):
    user_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User biometric and preference parameters")
    current_plan: Dict[str, Any] = Field(..., description="The current active meal plan dictionary")
    meal_name_to_swap: Optional[str] = Field(None, description="Name of the meal occasion to replace (e.g. 'Lunch')")
    meal_name: Optional[str] = Field(None, description="Alias for meal_name_to_swap")
    variation_seed: int = Field(1, description="Seed for picking alternative candidates")
    targets: Optional[Dict[str, float]] = Field(None, description="Target calories and macros")
    cuisine: Optional[str] = Field("indian", description="Cuisine preference")
    diet_type: Optional[str] = Field("vegetarian", description="Diet preference")
    allergies: Optional[List[str]] = Field(default_factory=list)
    user_prompt: Optional[str] = Field("")


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
        logging.error("Unhandled error generating meal plan: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the meal plan. Please verify your biometric parameters and try again."
        ) from exc


# Aliases for backwards compatibility
@app.post("/api/meal-plan/generate")
def generate_meal_plan_alias(request: PlanGenerationRequest):
    return generate_plan_endpoint(request)


@app.post("/generate-meal-plan")
def generate_meal_plan_root_alias(request: PlanGenerationRequest):
    """Root-level alias used by earlier frontend script versions."""
    return generate_plan_endpoint(request)


# =====================================================================
# INTERACTIVE REGENERATION & FOOD SWAPPING ENDPOINTS
# =====================================================================

@app.post("/api/plan/regenerate-alternative")
def regenerate_alternative_plan_endpoint(request: PlanGenerationRequest):
    """
    Generates a fresh, diverse meal plan by excluding previously shown food IDs
    and using deterministic seed variation.
    """
    return generate_plan_endpoint(request)


@app.post("/api/plan/alternatives")
def get_alternative_foods_endpoint(request: AlternativeFoodsRequest):
    """
    Retrieves wholesome alternative foods of the same functional role
    (e.g., swapping a staple grain for another staple).
    """
    try:
        alternatives = get_alternative_foods_for_item(
            fdc_id=request.fdc_id,
            diet_type=request.diet_type,
            cuisine=request.cuisine,
            allergies=request.allergies,
            disliked_foods=request.disliked_foods,
            eats_eggs=request.eats_eggs,
            limit=request.limit,
        )
        return {
            "status": "success",
            "fdc_id": request.fdc_id,
            "alternatives": alternatives
        }
    except Exception as exc:
        logging.error("Error fetching food alternatives: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/plan/swap-item")
def swap_item_endpoint(request: SwapItemRequest):
    """
    Replaces a single food item in an active meal plan, re-optimizes portion weights
    across the entire day, and re-synthesizes the recipe.
    """
    try:
        user_data = dict(request.user_data or {})
        if request.cuisine and "cuisine" not in user_data:
            user_data["cuisine"] = request.cuisine
        if request.diet_type and "diet_type" not in user_data:
            user_data["diet_type"] = request.diet_type
        if request.user_prompt and "user_prompt" not in user_data:
            user_data["user_prompt"] = request.user_prompt

        current_plan = dict(request.current_plan)
        if request.targets and "targets" not in current_plan:
            current_plan["targets"] = request.targets

        result = run_swap_item_pipeline(
            user_data=user_data,
            current_plan=current_plan,
            fdc_id_to_replace=request.fdc_id_to_replace,
            replacement_fdc_id=request.replacement_fdc_id
        )
        return {
            "status": "success",
            "plan": result,
            "meal_plan": result,
            "recipes": result.get("recipes", {})
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logging.error("Error swapping food item: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to swap food item.") from exc


@app.post("/api/plan/swap-meal")
def swap_meal_endpoint(request: SwapMealRequest):
    """
    Replaces all food items in a specific meal occasion (e.g. Lunch), re-optimizes
    portion weights, and re-synthesizes the recipe.
    """
    try:
        meal_name = request.meal_name_to_swap or request.meal_name or "Breakfast"
        user_data = dict(request.user_data or {})
        if request.cuisine and "cuisine" not in user_data:
            user_data["cuisine"] = request.cuisine
        if request.diet_type and "diet_type" not in user_data:
            user_data["diet_type"] = request.diet_type
        if request.allergies and "allergies" not in user_data:
            user_data["allergies"] = request.allergies
        if request.user_prompt and "user_prompt" not in user_data:
            user_data["user_prompt"] = request.user_prompt

        current_plan = dict(request.current_plan)
        if request.targets and "targets" not in current_plan:
            current_plan["targets"] = request.targets

        result = run_swap_meal_pipeline(
            user_data=user_data,
            current_plan=current_plan,
            meal_name_to_swap=meal_name,
            variation_seed=request.variation_seed
        )
        return {
            "status": "success",
            "plan": result,
            "meal_plan": result,
            "recipes": result.get("recipes", {}),
            "swapped_meal": meal_name
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logging.error("Error swapping meal occasion: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to swap meal.") from exc


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
