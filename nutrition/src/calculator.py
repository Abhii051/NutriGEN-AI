import sys
from pathlib import Path

# Add the project root to Python's path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from ai_model import generate_nutrition_profile


def calculate_nutrition(
    age,
    weight_kg,
    height_cm,
    sex,
    activity_level,
    goal
):
    """
    Calculate a complete nutrition profile
    using the NutriGEN-AI nutrition model.
    """

    return generate_nutrition_profile(
        age=age,
        weight_kg=weight_kg,
        height_cm=height_cm,
        sex=sex,
        activity_level=activity_level,
        goal=goal
    )


if __name__ == "__main__":

    print("\n===== NUTRIGEN-AI Nutrition Calculator =====")

    age = int(input("Enter age: "))
    weight = float(input("Enter weight (kg): "))
    height = float(input("Enter height (cm): "))
    sex = input("Enter sex (male/female): ")
    activity = input(
        "Enter activity level "
        "(sedentary/light/moderate/very_active/extremely_active): "
    )
    goal = input(
        "Enter goal "
        "(weight_loss/maintenance/weight_gain): "
    )

    profile = calculate_nutrition(
        age,
        weight,
        height,
        sex,
        activity,
        goal
    )

    print("\n===== NUTRITION RESULTS =====")

    print("BMR:", profile["bmr"], "kcal/day")
    print("TDEE:", profile["tdee"], "kcal/day")
    print("Calorie Target:", profile["calorie_target"], "kcal/day")

    print("Protein:", profile["protein_g"], "g/day")
    print("Fat:", profile["fat_g"], "g/day")
    print("Carbohydrates:", profile["carbs_g"], "g/day")