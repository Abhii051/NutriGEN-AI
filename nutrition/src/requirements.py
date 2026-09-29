import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from ai_model import generate_nutrition_profile


def get_nutrition_requirements(
    age,
    weight_kg,
    height_cm,
    sex,
    activity_level,
    goal
):
    profile = generate_nutrition_profile(
        age=age,
        weight_kg=weight_kg,
        height_cm=height_cm,
        sex=sex,
        activity_level=activity_level,
        goal=goal
    )

    requirements = {
        "calories": profile["calorie_target"],
        "protein_g": profile["protein_g"],
        "fat_g": profile["fat_g"],
        "carbs_g": profile["carbs_g"]
    }

    return requirements


if __name__ == "__main__":
    result = get_nutrition_requirements(
        age=20,
        weight_kg=70,
        height_cm=175,
        sex="male",
        activity_level="moderate",
        goal="maintenance"
    )

    print("\n===== NUTRITION REQUIREMENTS =====")
    print("Calories:", result["calories"], "kcal/day")
    print("Protein:", result["protein_g"], "g/day")
    print("Fat:", result["fat_g"], "g/day")
    print("Carbohydrates:", result["carbs_g"], "g/day")