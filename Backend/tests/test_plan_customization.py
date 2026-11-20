"""
NutriGEN-AI: Plan Customization & Interactive Editing Tests
Verifies:
1. Plan regeneration with zero-overlap alternative foods
2. Individual food item swapping with macro re-balancing
3. Entire meal occasion swapping with macro re-balancing
4. Multi-day plan generation (Day 1, Day 2, Day 3) with ingredient variety
"""

import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Backend.src.optimizer import (
    generate_meal_plan,
    get_alternative_foods_for_item,
    swap_food_in_plan,
    swap_entire_meal_in_plan,
    generate_multi_day_plan,
)
from Backend.src.pipeline import (
    run_nutrigen_pipeline,
    run_swap_item_pipeline,
    run_swap_meal_pipeline
)


class TestPlanCustomization(unittest.TestCase):

    def setUp(self):
        self.user_data = {
            "age": 24,
            "sex": "male",
            "height_cm": 178.0,
            "weight_kg": 74.0,
            "activity_level": "moderate",
            "goal": "maintenance",
            "diet_type": "vegetarian",
            "cuisine": "indian",
            "allergies": ["peanuts"],
            "disliked_foods": [],
            "eats_eggs": False,
            "number_of_meals": 3,
            "number_of_snacks": 1,
        }

    def test_regenerate_alternative_plan_zero_overlap(self):
        """Verifies that an alternative plan has zero overlap with the original plan."""
        # 1. Generate base plan
        res1 = run_nutrigen_pipeline(self.user_data)
        plan1 = res1["meal_plan"]
        ids1 = set(f["fdc_id"] for meal in plan1["meal_plan"].values() for f in meal)

        # 2. Regenerate with exclude_fdc_ids
        alt_user_data = dict(self.user_data)
        alt_user_data["exclude_fdc_ids"] = list(ids1)
        alt_user_data["variation_seed"] = 42

        res2 = run_nutrigen_pipeline(alt_user_data)
        plan2 = res2["meal_plan"]
        ids2 = set(f["fdc_id"] for meal in plan2["meal_plan"].values() for f in meal)

        overlap = ids1.intersection(ids2)
        self.assertEqual(len(overlap), 0, f"Alternative plan must have zero overlap, got {overlap}")
        self.assertLessEqual(plan2["optimization"]["calorie_error_percent"], 5.0)

    def test_alternative_foods_lookup(self):
        """Verifies that alternatives for a food item share the same functional role."""
        res = run_nutrigen_pipeline(self.user_data)
        first_item = list(res["meal_plan"]["meal_plan"].values())[0][0]
        fdc_id = first_item["fdc_id"]
        role = first_item["food_role"]

        alts = get_alternative_foods_for_item(
            fdc_id=fdc_id,
            diet_type="vegetarian",
            cuisine="indian",
            limit=5
        )
        self.assertGreaterEqual(len(alts), 1)
        for a in alts:
            self.assertEqual(a["food_role"], role)
            self.assertNotEqual(a["fdc_id"], fdc_id)

    def test_single_food_swap_preserves_macros(self):
        """Verifies swapping a food item keeps total calories within 5% tolerance."""
        res = run_nutrigen_pipeline(self.user_data)
        plan = res["meal_plan"]
        first_item = list(plan["meal_plan"].values())[0][0]
        fdc_id = first_item["fdc_id"]

        swapped = run_swap_item_pipeline(
            user_data=self.user_data,
            current_plan=plan,
            fdc_id_to_replace=fdc_id
        )

        self.assertNotEqual(swapped["replaced_fdc_id"], swapped["new_fdc_id"])
        self.assertLessEqual(swapped["optimization"]["calorie_error_percent"], 5.0)

    def test_meal_swap_preserves_macros(self):
        """Verifies swapping an entire meal occasion keeps total calories within 5% tolerance."""
        res = run_nutrigen_pipeline(self.user_data)
        plan = res["meal_plan"]

        swapped_meal = run_swap_meal_pipeline(
            user_data=self.user_data,
            current_plan=plan,
            meal_name_to_swap="Lunch",
            variation_seed=7
        )

        self.assertEqual(swapped_meal["swapped_meal"], "Lunch")
        self.assertLessEqual(swapped_meal["optimization"]["calorie_error_percent"], 5.0)

    def test_multi_day_plan_generation(self):
        """Verifies generating a 3-day plan produces 3 distinct daily meal plans."""
        multi_data = dict(self.user_data)
        multi_data["plan_days"] = 3

        res = run_nutrigen_pipeline(multi_data)
        self.assertTrue(res["meal_plan"]["multi_day"])
        self.assertEqual(res["meal_plan"]["total_days"], 3)
        self.assertEqual(len(res["meal_plan"]["days"]), 3)

        day1_foods = set(f["fdc_id"] for m in res["meal_plan"]["days"][0]["meal_plan"].values() for f in m)
        day2_foods = set(f["fdc_id"] for m in res["meal_plan"]["days"][1]["meal_plan"].values() for f in m)
        # Verify days rotate ingredients
        self.assertNotEqual(day1_foods, day2_foods)


if __name__ == "__main__":
    unittest.main()
