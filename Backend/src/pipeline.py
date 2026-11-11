"""
NutriGEN-AI: Layer 3 Pipeline Orchestrator & LLM Recipe Generator
Integrates Biometrics Engine (Pratheek) -> Optimizer Engine (Abhinav) -> Groq Llama 3.1 8B LLM Recipe Generator
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nutrigen.pipeline")

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
import sys
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import Layer 1 & 2 verified modules
try:
    from ai_model import generate_nutrition_profile
except ImportError:
    from src.ai_model import generate_nutrition_profile

from Backend.src.optimizer import generate_meal_plan
from Backend.src.recipe_generator import (
    generate_recipe_for_meal,
    generate_fallback_recipe,
    clean_food_name,
    PRIMARY_GROQ_MODEL
)


# =====================================================================
# MAIN PIPELINE ORCHESTRATOR
# =====================================================================

def run_nutrigen_pipeline(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the end-to-end NutriGEN-AI Layer 3 Pipeline:
    1. Biometrics & Macro Calculation (ai_model.py)
    2. Meal Plan Optimization (Backend/src/optimizer.py)
    3. Groq Llama 3.1 8B Recipe Generation with cooking instruction attachment
    """
    # 1. Parse and normalize user data
    age = int(user_data.get("age", 22))
    sex = str(user_data.get("sex", "male")).lower().strip()
    height_cm = float(user_data.get("height_cm", 175.0))
    weight_kg = float(user_data.get("weight_kg", 70.0))
    
    # Normalize activity level
    activity_map = {
        "sedentary": "sedentary",
        "light": "light",
        "lightly active": "light",
        "moderate": "moderate",
        "moderately active": "moderate",
        "very_active": "very_active",
        "very active": "very_active",
        "extremely_active": "extremely_active",
        "extremely active": "extremely_active"
    }
    raw_activity = str(user_data.get("activity_level", "moderate")).lower().strip()
    activity_level = activity_map.get(raw_activity, "moderate")

    # Normalize goal
    goal_map = {
        "weight_loss": "weight_loss",
        "weight loss": "weight_loss",
        "lose weight": "weight_loss",
        "maintenance": "maintenance",
        "maintain weight": "maintenance",
        "weight_gain": "weight_gain",
        "weight gain": "weight_gain",
        "gain weight": "weight_gain",
    }
    raw_goal = str(user_data.get("goal", "maintenance")).lower().strip()
    goal = goal_map.get(raw_goal, "maintenance")

    # Dietary preferences
    raw_diet = str(user_data.get("diet_type", "vegetarian")).lower().strip().replace("_", "-")
    diet_type = "non-vegetarian" if "non" in raw_diet else raw_diet
    if diet_type not in ["vegetarian", "vegan", "non-vegetarian"]:
        diet_type = "vegetarian"

    cuisine = str(user_data.get("cuisine", "indian")).lower().strip()
    eats_eggs = bool(user_data.get("eats_eggs", False))
    allergies = user_data.get("allergies", [])
    if isinstance(allergies, str):
        allergies = [a.strip() for a in allergies.split(",") if a.strip()]

    disliked_foods = user_data.get("disliked_foods", [])
    if isinstance(disliked_foods, str):
        disliked_foods = [d.strip() for d in disliked_foods.split(",") if d.strip()]

    number_of_meals = int(user_data.get("number_of_meals", 3))
    number_of_snacks = int(user_data.get("number_of_snacks", 1))
    user_prompt = str(user_data.get("user_prompt", "")).strip()
    groq_api_key = user_data.get("groq_api_key") or os.getenv("GROQ_API_KEY")

    raw_target_weight = user_data.get("target_weight_kg")
    target_weight_kg = float(raw_target_weight) if raw_target_weight not in [None, "", 0] else None

    # 2. Compute Biometrics & Nutritional Targets (Layer 1 Pratheek)
    profile = generate_nutrition_profile(
        age=age,
        weight_kg=weight_kg,
        height_cm=height_cm,
        sex=sex,
        activity_level=activity_level,
        goal=goal
    )

    targets = {
        "calories": profile["calorie_target"],
        "protein_g": profile["protein_g"],
        "fat_g": profile["fat_g"],
        "carbs_g": profile["carbs_g"],
    }

    # 3. Numerical Optimization Engine (Layer 2 Abhinav)
    plan = generate_meal_plan(
        target_calories=targets["calories"],
        target_protein=targets["protein_g"],
        target_fat=targets["fat_g"],
        target_carbs=targets["carbs_g"],
        diet_type=diet_type,
        allergies=allergies,
        disliked_foods=disliked_foods,
        cuisine=cuisine,
        eats_eggs=eats_eggs,
        number_of_meals=number_of_meals,
        number_of_snacks=number_of_snacks,
    )

    # 4. Generate Recipes for each meal via Groq Llama 3.1 (or fallback)
    recipes = {}
    for meal_name, items in plan["meal_plan"].items():
        recipe = generate_recipe_for_meal(
            meal_type=meal_name,
            food_items=items,
            user_prompt=user_prompt,
            cuisine=cuisine,
            diet_type=diet_type,
            groq_api_key=groq_api_key
        )
        recipes[meal_name] = recipe

    # Attach recipes into the meal_plan object
    plan["recipes"] = recipes

    # 5. Calculate Clinical Biometrics & Target Projections
    bmi = round(weight_kg / ((height_cm / 100.0) ** 2), 1)
    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25.0:
        bmi_category = "Normal weight"
    elif bmi < 30.0:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"

    cal_target = profile["calorie_target"]
    tdee_val = profile["tdee"]
    daily_delta = round(cal_target - tdee_val, 0)
    water_intake_l = round(weight_kg * 0.035, 1)

    weight_delta_kg = None
    weekly_rate_kg = None
    estimated_weeks = None

    if target_weight_kg is not None:
        weight_delta_kg = round(target_weight_kg - weight_kg, 1)
        weekly_rate_kg = round(abs(daily_delta) * 7.0 / 7700.0, 2) if daily_delta != 0 else 0.0
        if weekly_rate_kg > 0 and weight_delta_kg != 0:
            estimated_weeks = round(abs(weight_delta_kg) / weekly_rate_kg, 1)
        elif weight_delta_kg == 0:
            estimated_weeks = 0.0

    biometrics = {
        "bmr": round(profile["bmr"], 1),
        "tdee": round(profile["tdee"], 1),
        "bmi": bmi,
        "bmi_category": bmi_category,
        "current_weight_kg": weight_kg,
        "target_weight_kg": target_weight_kg,
        "weight_delta_kg": weight_delta_kg,
        "daily_calorie_delta": daily_delta,
        "weekly_rate_kg": weekly_rate_kg,
        "estimated_weeks": estimated_weeks,
        "water_intake_liters": water_intake_l
    }

    # 6. Build Final Response Payload
    return {
        "status": "success",
        "llm_engine": f"Groq {PRIMARY_GROQ_MODEL}",
        "biometrics": biometrics,
        "nutrition_requirements": {
            "bmr": profile["bmr"],
            "tdee": profile["tdee"],
            "calories": profile["calorie_target"],
            "protein_g": profile["protein_g"],
            "fat_g": profile["fat_g"],
            "carbs_g": profile["carbs_g"],
        },
        "meal_plan": plan,
        "recipes": recipes
    }


if __name__ == "__main__":
    test_data = {
        "age": 22,
        "sex": "male",
        "height_cm": 175.0,
        "weight_kg": 70.0,
        "activity_level": "moderate",
        "goal": "maintenance",
        "diet_type": "vegetarian",
        "allergies": ["peanuts"],
        "disliked_foods": [],
        "cuisine": "indian",
        "user_prompt": "Quick 15-minute meals, spicy, no oven"
    }
    output = run_nutrigen_pipeline(test_data)
    print(json.dumps(output, indent=2))
