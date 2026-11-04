"""
Unit & Integration Tests for NutriGEN-AI Layer 3 REST API & Pipeline
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Backend.server import app, health_check, generate_plan_endpoint, PlanGenerationRequest
from Backend.src.pipeline import run_nutrigen_pipeline, generate_fallback_recipe


def test_health_endpoint():
    data = health_check()
    assert data["status"] == "healthy"
    assert "NutriGEN-AI" in data["service"]


def test_generate_plan_endpoint():
    request = PlanGenerationRequest(
        age=22,
        sex="male",
        height_cm=175.0,
        weight_kg=70.0,
        activity_level="moderate",
        goal="maintenance",
        diet_type="vegetarian",
        allergies=["peanuts"],
        disliked_foods=[],
        cuisine="indian",
        user_prompt="Quick 15-minute meals, spicy, no oven"
    )
    data = generate_plan_endpoint(request)

    # Verify status
    assert data["status"] == "success"

    # Verify nutrition targets
    reqs = data["nutrition_requirements"]
    assert reqs["calories"] > 0
    assert reqs["protein_g"] > 0
    assert reqs["fat_g"] > 0
    assert reqs["carbs_g"] > 0

    # Verify meal plan
    plan = data["meal_plan"]
    assert plan["total_foods"] <= 14
    assert "Breakfast" in plan["meal_plan"]
    assert "Lunch" in plan["meal_plan"]
    assert "Dinner" in plan["meal_plan"]

    # Verify recipes
    assert "recipes" in data
    assert "Breakfast" in data["recipes"]
    breakfast_recipe = data["recipes"]["Breakfast"]
    assert "dish_title" in breakfast_recipe
    assert "cooking_time" in breakfast_recipe
    assert len(breakfast_recipe["instructions"]) == 3
    print("Plan and recipes verified successfully!")


def test_fallback_recipe_generation():
    food_items = [
        {"food": "Millet, raw", "grams": 140.0, "calories": 530.0, "food_role": "staple"},
        {"food": "Chickpea flour (besan)", "grams": 40.0, "calories": 150.0, "food_role": "protein"},
    ]
    recipe = generate_fallback_recipe("Breakfast", food_items, user_prompt="15 mins spicy no oven")
    assert "dish_title" in recipe
    assert "15 mins" in recipe["cooking_time"]
    assert len(recipe["instructions"]) == 3


if __name__ == "__main__":
    print("Testing health endpoint...")
    test_health_endpoint()
    print("Health endpoint PASSED.")

    print("Testing recipe fallback generation...")
    test_fallback_recipe_generation()
    print("Recipe fallback generation PASSED.")

    print("Testing full plan generation endpoint...")
    test_generate_plan_endpoint()
    print("Full plan generation endpoint PASSED.")
    print("\nALL API TESTS PASSED SUCCESSFULLY!")
