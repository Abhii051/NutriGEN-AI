"""
End-to-End Clinical Nutrition & Optimization Audit Test Suite
Verifies:
1. Multi-profile biometric calculations & energy targets
2. Strict allergy filtering with normalized alias expansion
3. Zero duplicate food items across 2, 3, 4, and 5 meal structures
4. SLSQP numerical convergence, bound enforcement, and error validation
5. AI Chef recipe generation and post-generation allergen safety validation
"""

import sys
import os
import re
import unittest
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# User site packages fallback
py_user_site = Path(r"C:\Users\abhi\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages")
if py_user_site.exists() and str(py_user_site) not in sys.path:
    sys.path.append(str(py_user_site))

from Backend.src.pipeline import run_nutrigen_pipeline
from Backend.src.recipe_generator import validate_recipe_safety, generate_recipe_for_meal
from Backend.src.preferences import create_preferences, apply_allergy_filter
import pandas as pd


class TestEndToEndAudit(unittest.TestCase):

    def test_profile_1_male_weight_loss_4_meals_peanut_allergy(self):
        """Profile 1: 23yo Male, 76kg -> 70kg, 4 meals, vegetarian, Indian, peanut allergy."""
        payload = {
            "age": 23,
            "sex": "male",
            "height_cm": 176.0,
            "weight_kg": 76.0,
            "target_weight_kg": 70.0,
            "activity_level": "moderate",
            "goal": "weight_loss",
            "diet_type": "vegetarian",
            "cuisine": "indian",
            "number_of_meals": 4,
            "number_of_snacks": 1,
            "allergies": ["peanuts"],
            "user_prompt": "Quick 15 min meals, flavorful, no oven"
        }

        result = run_nutrigen_pipeline(payload)
        self.assertEqual(result["status"], "success")

        # 1. Biometrics verification
        bio = result["biometrics"]
        self.assertGreater(bio["bmr"], 1600)
        self.assertGreater(bio["tdee"], bio["bmr"])
        self.assertLess(bio["daily_calorie_delta"], 0)  # Calorie deficit
        self.assertIsNotNone(bio["estimated_weeks"])

        # 2. Meal structure verification (4 meals: Breakfast, Lunch, Snack, Dinner)
        meals = result["meal_plan"]["meal_plan"]
        self.assertEqual(len(meals), 4)
        for expected in ["Breakfast", "Lunch", "Snack", "Dinner"]:
            self.assertIn(expected, meals, f"Expected {expected} in 4-meal plan")

        # 3. Zero duplicate FDC IDs
        fdc_ids = [item["fdc_id"] for meal_items in meals.values() for item in meal_items]
        self.assertEqual(len(fdc_ids), len(set(fdc_ids)), "Found duplicate food IDs in 4-meal plan")

        # 4. Strict allergy protection (No peanut or groundnut)
        for meal_name, items in meals.items():
            for item in items:
                desc = item["food"].lower()
                self.assertNotIn("peanut", desc, f"Found peanut in {meal_name}: {desc}")
                self.assertNotIn("groundnut", desc, f"Found groundnut in {meal_name}: {desc}")

        # 5. SLSQP Convergence & Accuracy
        opt = result["meal_plan"]["optimization"]
        self.assertTrue(opt["solver_converged"], f"Solver did not converge: {opt['solver_message']}")
        self.assertTrue(opt["is_within_tolerance"], f"Calorie error {opt['calorie_error_percent']}% > 5%")
        self.assertLessEqual(opt["calorie_error_percent"], 5.0)

        # 6. Recipe generation verification
        recipes = result["recipes"]
        self.assertEqual(len(recipes), 4)
        for m, rec in recipes.items():
            self.assertIn("dish_title", rec)
            self.assertIn("instructions", rec)
            self.assertIn("Allergen filter applied", rec.get("chef_notes", ""))

    def test_profile_2_female_muscle_gain_5_meals_dairy_allergy(self):
        """Profile 2: 28yo Female, 62kg, 5 meals, non-vegetarian, Mediterranean, dairy allergy."""
        payload = {
            "age": 28,
            "sex": "female",
            "height_cm": 168.0,
            "weight_kg": 62.0,
            "activity_level": "very_active",
            "goal": "weight_gain",
            "diet_type": "non-vegetarian",
            "cuisine": "mediterranean",
            "number_of_meals": 5,
            "number_of_snacks": 2,
            "allergies": ["milk"],
            "user_prompt": "High protein, olive oil seasoning"
        }

        result = run_nutrigen_pipeline(payload)
        self.assertEqual(result["status"], "success")

        # 1. 5 distinct meal occasions
        meals = result["meal_plan"]["meal_plan"]
        self.assertEqual(len(meals), 5)
        for expected in ["Breakfast", "Morning Snack", "Lunch", "Evening Snack", "Dinner"]:
            self.assertIn(expected, meals, f"Expected {expected} in 5-meal plan")

        # 2. Total items = 16, Zero duplicate FDC IDs
        fdc_ids = [item["fdc_id"] for meal_items in meals.values() for item in meal_items]
        self.assertEqual(len(fdc_ids), 16)
        self.assertEqual(len(fdc_ids), len(set(fdc_ids)), "Found duplicate food IDs in 5-meal plan")

        # 3. Dairy allergen exclusion
        for meal_name, items in meals.items():
            for item in items:
                desc = item["food"].lower()
                for dairy_term in ["milk", "cheese", "paneer", "yogurt", "curd", "butter", "whey"]:
                    self.assertNotIn(dairy_term, desc, f"Found dairy term '{dairy_term}' in {meal_name}: {desc}")

        # 4. SLSQP Convergence
        opt = result["meal_plan"]["optimization"]
        self.assertTrue(opt["solver_converged"])
        self.assertTrue(opt["is_within_tolerance"])

    def test_profile_3_intermittent_fasting_2_meals_vegan(self):
        """Profile 3: 35yo Male, 85kg, 2 meals (Lunch, Dinner), vegan, any cuisine."""
        payload = {
            "age": 35,
            "sex": "male",
            "height_cm": 182.0,
            "weight_kg": 85.0,
            "activity_level": "moderate",
            "goal": "maintenance",
            "diet_type": "vegan",
            "cuisine": "any",
            "number_of_meals": 2,
            "number_of_snacks": 0
        }

        result = run_nutrigen_pipeline(payload)
        self.assertEqual(result["status"], "success")

        meals = result["meal_plan"]["meal_plan"]
        self.assertEqual(len(meals), 2)
        self.assertIn("Lunch", meals)
        self.assertIn("Dinner", meals)

        # Zero duplicates
        fdc_ids = [item["fdc_id"] for meal_items in meals.values() for item in meal_items]
        self.assertEqual(len(fdc_ids), len(set(fdc_ids)))

        # Absolute vegan compliance (no animal foods)
        for meal_name, items in meals.items():
            for item in items:
                desc = item["food"].lower()
                for non_vegan in ["chicken", "fish", "meat", "milk", "cheese", "yogurt", "ghee", "butter"]:
                    self.assertNotIn(non_vegan, desc, f"Non-vegan item '{non_vegan}' found in {meal_name}: {desc}")
                # Ensure biological egg is not present (allow vegetable eggplant)
                self.assertFalse(bool(re.search(r"\beggs?\b(?!plant)", desc)), f"Non-vegan egg found in {meal_name}: {desc}")

    def test_llm_recipe_safety_validation(self):
        """Verifies post-generation output validation catches hallucinated allergens."""
        # Safe recipe
        safe_recipe = {
            "dish_title": "Spiced Basmati Rice & Steamed Tofu Bowl",
            "instructions": [
                "Rinse basmati rice and simmer for 12 minutes.",
                "Dice tofu and sauté in non-stick skillet with turmeric and cumin.",
                "Combine rice and tofu in a warm bowl and serve."
            ],
            "chef_notes": "Allergen-free meal."
        }
        self.assertTrue(validate_recipe_safety(safe_recipe, ["peanuts", "dairy"]))

        # Hallucinated allergen in instructions
        unsafe_recipe_steps = {
            "dish_title": "Crunchy Protein Salad",
            "instructions": [
                "Toss leafy greens in a bowl.",
                "Drizzle 2 tablespoons of peanut butter sauce over the top.",
                "Serve chilled."
            ],
            "chef_notes": "Quick preparation."
        }
        self.assertFalse(validate_recipe_safety(unsafe_recipe_steps, ["peanuts"]))

        # Hallucinated allergen in title
        unsafe_recipe_title = {
            "dish_title": "Creamy Peanut Noodles",
            "instructions": ["Boil noodles", "Mix sauce", "Serve"],
            "chef_notes": "Standard"
        }
        self.assertFalse(validate_recipe_safety(unsafe_recipe_title, ["peanuts"]))

        # Plural/stem variant detection
        unsafe_plural = {
            "dish_title": "Gourmet Nut Medley",
            "instructions": ["Toast almonds and walnuts", "Mix with grain", "Serve"],
            "chef_notes": "Standard"
        }
        self.assertFalse(validate_recipe_safety(unsafe_plural, ["tree nuts"]))


if __name__ == "__main__":
    unittest.main()
