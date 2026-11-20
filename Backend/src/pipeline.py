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

from Backend.src.optimizer import (
    generate_meal_plan,
    get_alternative_foods_for_item,
    swap_food_in_plan,
    swap_entire_meal_in_plan,
    generate_multi_day_plan,
)
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
        "active": "very_active",
        "very_active": "very_active",
        "very active": "very_active",
        "extremely": "extremely_active",
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

    # Multi-day and regeneration parameters
    exclude_fdc_ids = user_data.get("exclude_fdc_ids", [])
    if isinstance(exclude_fdc_ids, str):
        exclude_fdc_ids = [int(x.strip()) for x in exclude_fdc_ids.split(",") if x.strip().isdigit()]
    variation_seed = int(user_data.get("variation_seed", 0))
    plan_days = int(user_data.get("plan_days", 1))
    plan_days = max(1, min(7, plan_days))

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
    if plan_days > 1:
        multi_days = generate_multi_day_plan(
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
            plan_days=plan_days,
            start_seed=variation_seed,
        )
        for day_obj in multi_days:
            day_recipes = {}
            for m_name, items in day_obj["meal_plan"].items():
                day_recipes[m_name] = generate_recipe_for_meal(
                    meal_type=m_name,
                    food_items=items,
                    user_prompt=user_prompt,
                    cuisine=cuisine,
                    diet_type=diet_type,
                    allergies=allergies,
                    groq_api_key=groq_api_key
                )
            day_obj["recipes"] = day_recipes

        plan = {
            "diet_type": diet_type,
            "targets": targets,
            "totals": multi_days[0]["totals"],
            "meal_plan": multi_days[0]["meal_plan"],
            "recipes": multi_days[0]["recipes"],
            "optimization": multi_days[0]["optimization"],
            "multi_day": True,
            "total_days": plan_days,
            "days": multi_days,
        }
    else:
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
            exclude_fdc_ids=exclude_fdc_ids,
            variation_seed=variation_seed,
        )

        recipes = {}
        for meal_name, items in plan["meal_plan"].items():
            recipe = generate_recipe_for_meal(
                meal_type=meal_name,
                food_items=items,
                user_prompt=user_prompt,
                cuisine=cuisine,
                diet_type=diet_type,
                allergies=allergies,
                groq_api_key=groq_api_key
            )
            recipes[meal_name] = recipe

        plan["recipes"] = recipes
        plan["multi_day"] = False
        plan["total_days"] = 1
        plan["days"] = [{
            "day_number": 1,
            "day_label": "Day 1",
            "meal_plan": plan["meal_plan"],
            "recipes": plan["recipes"],
            "totals": plan["totals"],
            "optimization": plan["optimization"],
        }]

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

    # 6. Determine Effective Engine & Build Final Response Payload
    recipes = plan.get("recipes", {})
    recipe_engines = [r.get("engine") for r in recipes.values() if r.get("engine")]
    effective_engine = recipe_engines[0] if recipe_engines else "Heuristic Precision Engine"

    return {
        "status": "success",
        "llm_engine": effective_engine,
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


def run_swap_item_pipeline(
    user_data: Dict[str, Any],
    current_plan: Dict[str, Any],
    fdc_id_to_replace: int,
    replacement_fdc_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Executes an item-level swap in the active meal plan and re-synthesizes the recipe.
    """
    targets = current_plan.get("targets", {})
    if not targets:
        profile = generate_nutrition_profile(
            age=int(user_data.get("age", 22)),
            weight_kg=float(user_data.get("weight_kg", 70.0)),
            height_cm=float(user_data.get("height_cm", 175.0)),
            sex=str(user_data.get("sex", "male")),
            activity_level=str(user_data.get("activity_level", "moderate")),
            goal=str(user_data.get("goal", "maintenance"))
        )
        targets = {
            "calories": profile["calorie_target"],
            "protein_g": profile["protein_g"],
            "fat_g": profile["fat_g"],
            "carbs_g": profile["carbs_g"],
        }

    raw_diet = str(user_data.get("diet_type", "vegetarian")).lower().strip().replace("_", "-")
    diet_type = "non-vegetarian" if "non" in raw_diet else raw_diet
    cuisine = str(user_data.get("cuisine", "indian")).lower().strip()
    allergies = user_data.get("allergies", [])
    if isinstance(allergies, str):
        allergies = [a.strip() for a in allergies.split(",") if a.strip()]
    disliked_foods = user_data.get("disliked_foods", [])
    eats_eggs = bool(user_data.get("eats_eggs", False))

    updated_plan = swap_food_in_plan(
        current_plan=current_plan,
        targets=targets,
        fdc_id_to_replace=fdc_id_to_replace,
        replacement_fdc_id=replacement_fdc_id,
        diet_type=diet_type,
        cuisine=cuisine,
        allergies=allergies,
        disliked_foods=disliked_foods,
        eats_eggs=eats_eggs,
    )

    swapped_meal = updated_plan["swapped_meal"]
    groq_api_key = user_data.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    user_prompt = str(user_data.get("user_prompt", "")).strip()

    recipes = dict(current_plan.get("recipes", {}))
    new_meal_items = updated_plan["meal_plan"].get(swapped_meal, [])
    new_recipe = generate_recipe_for_meal(
        meal_type=swapped_meal,
        food_items=new_meal_items,
        user_prompt=user_prompt,
        cuisine=cuisine,
        diet_type=diet_type,
        allergies=allergies,
        groq_api_key=groq_api_key
    )
    recipes[swapped_meal] = new_recipe
    updated_plan["recipes"] = recipes

    return updated_plan


def run_swap_meal_pipeline(
    user_data: Dict[str, Any],
    current_plan: Dict[str, Any],
    meal_name_to_swap: str,
    variation_seed: int = 1,
) -> Dict[str, Any]:
    """
    Executes a meal-level swap in the active meal plan and re-synthesizes the recipe.
    """
    targets = current_plan.get("targets", {})
    if not targets:
        profile = generate_nutrition_profile(
            age=int(user_data.get("age", 22)),
            weight_kg=float(user_data.get("weight_kg", 70.0)),
            height_cm=float(user_data.get("height_cm", 175.0)),
            sex=str(user_data.get("sex", "male")),
            activity_level=str(user_data.get("activity_level", "moderate")),
            goal=str(user_data.get("goal", "maintenance"))
        )
        targets = {
            "calories": profile["calorie_target"],
            "protein_g": profile["protein_g"],
            "fat_g": profile["fat_g"],
            "carbs_g": profile["carbs_g"],
        }

    raw_diet = str(user_data.get("diet_type", "vegetarian")).lower().strip().replace("_", "-")
    diet_type = "non-vegetarian" if "non" in raw_diet else raw_diet
    cuisine = str(user_data.get("cuisine", "indian")).lower().strip()
    allergies = user_data.get("allergies", [])
    if isinstance(allergies, str):
        allergies = [a.strip() for a in allergies.split(",") if a.strip()]
    disliked_foods = user_data.get("disliked_foods", [])
    eats_eggs = bool(user_data.get("eats_eggs", False))

    updated_plan = swap_entire_meal_in_plan(
        current_plan=current_plan,
        targets=targets,
        meal_name_to_swap=meal_name_to_swap,
        diet_type=diet_type,
        cuisine=cuisine,
        allergies=allergies,
        disliked_foods=disliked_foods,
        eats_eggs=eats_eggs,
        variation_seed=variation_seed,
    )

    groq_api_key = user_data.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    user_prompt = str(user_data.get("user_prompt", "")).strip()

    recipes = dict(current_plan.get("recipes", {}))
    new_meal_items = updated_plan["meal_plan"].get(meal_name_to_swap, [])
    new_recipe = generate_recipe_for_meal(
        meal_type=meal_name_to_swap,
        food_items=new_meal_items,
        user_prompt=user_prompt,
        cuisine=cuisine,
        diet_type=diet_type,
        allergies=allergies,
        groq_api_key=groq_api_key
    )
    recipes[meal_name_to_swap] = new_recipe
    updated_plan["recipes"] = recipes

    return updated_plan


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
