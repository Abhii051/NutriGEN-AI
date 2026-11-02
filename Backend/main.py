from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_DIR = PROJECT_ROOT / "src"
NUTRITION_DIR = PROJECT_ROOT / "nutrition" / "src"

sys.path.insert(0, str(MODEL_DIR))
sys.path.insert(0, str(NUTRITION_DIR))


from calculator import calculate_nutrition
from requirements import get_nutrition_requirements


app = FastAPI(
    title="NutriGEN-AI API",
    description="API for nutrition profile calculations",
    version="1.0.0"
)


class NutritionRequest(BaseModel):

    age: int = Field(gt=0, le=120)

    weight_kg: float = Field(gt=0)

    height_cm: float = Field(gt=0)

    sex: Literal["male", "female"]

    activity_level: Literal[
        "sedentary",
        "light",
        "moderate",
        "very_active",
        "extremely_active"
    ]

    goal: Literal[
        "weight_loss",
        "maintenance",
        "weight_gain"
    ]



#Home endpoint


@app.get("/")
def home():

    return {
        "message": "Welcome to NutriGEN-AI API",
        "status": "running"
    }



@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


@app.post("/api/nutrition/calculate")
def calculate_nutrition_endpoint(request: NutritionRequest):

    try:

        profile = calculate_nutrition(
            age=request.age,
            weight_kg=request.weight_kg,
            height_cm=request.height_cm,
            sex=request.sex,
            activity_level=request.activity_level,
            goal=request.goal
        )

        return {
            "status": "success",
            "nutrition_profile": profile
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="An error occurred during nutrition calculation."
        ) from exc

@app.post("/api/nutrition/requirements")
def nutrition_requirements_endpoint(request: NutritionRequest):

    try:
        requirements = get_nutrition_requirements(
            age=request.age,
            weight_kg=request.weight_kg,
            height_cm=request.height_cm,
            sex=request.sex,
            activity_level=request.activity_level,
            goal=request.goal
        )

        return {
            "status": "success",
            "nutrition_requirements": requirements
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while calculating nutrition requirements."
        ) from exc