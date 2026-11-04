"""
Test Groq Llama 3.1 8B Recipe Generation Engine
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Backend.src.recipe_generator import (
    generate_recipe_for_meal,
    clean_food_name,
    generate_fallback_recipe,
    PRIMARY_GROQ_MODEL
)


def test_clean_food_name():
    raw_name = "Cereals ready-to-eat, QUAKER, 100% Natural Granola, Oats, Wheat and Honey"
    cleaned = clean_food_name(raw_name)
    assert "Cereals ready-to-eat" not in cleaned
    assert "Quaker" in cleaned or "Granola" in cleaned
    print("clean_food_name PASSED.")


def test_recipe_generation_with_custom_prompt():
    sample_foods = [
        {"food": "Millet, raw", "grams": 143.2, "calories": 541.3, "food_role": "staple"},
        {"food": "Chickpea flour (besan)", "grams": 40.0, "calories": 154.8, "food_role": "protein"},
        {"food": "Groundcherries, (cape-gooseberries or poha), raw", "grams": 81.6, "calories": 43.2, "food_role": "fruit"},
        {"food": "Beverages, rice milk, unsweetened", "grams": 173.4, "calories": 81.5, "food_role": "dairy"},
    ]
    user_prompt = "Quick 15-minute meals, spicy, no oven"

    recipe = generate_recipe_for_meal(
        meal_type="Breakfast",
        food_items=sample_foods,
        user_prompt=user_prompt,
        cuisine="indian",
        diet_type="vegetarian"
    )

    assert "dish_title" in recipe
    assert "cooking_time" in recipe
    assert "instructions" in recipe
    assert len(recipe["instructions"]) == 3
    assert "15 mins" in recipe["cooking_time"]

    print("\nGenerated Recipe Sample:")
    print("Title:", recipe["dish_title"])
    print("Cook Time:", recipe["cooking_time"])
    print("Engine:", recipe.get("engine"))
    for idx, step in enumerate(recipe["instructions"], 1):
        print(f"Step {idx}: {step}")

    print("recipe_generation_with_custom_prompt PASSED.")


if __name__ == "__main__":
    test_clean_food_name()
    test_recipe_generation_with_custom_prompt()
    print("\nALL GROQ RECIPE TESTS PASSED!")
