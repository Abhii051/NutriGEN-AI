import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from ai_model import (
    calculate_bmr,
    calculate_tdee,
    calculate_calorie_target,
    calculate_macros,
    generate_nutrition_profile
)

from nutrition.src.calculator import calculate_nutrition


def test_bmr():
    result = calculate_bmr(20, 70, 175, "male")
    assert result > 0


def test_tdee():
    bmr = calculate_bmr(20, 70, 175, "male")
    result = calculate_tdee(bmr, "moderate")
    assert result > bmr


def test_calorie_target():
    tdee = 2500

    loss = calculate_calorie_target(tdee, "weight_loss")
    maintenance = calculate_calorie_target(tdee, "maintenance")
    gain = calculate_calorie_target(tdee, "weight_gain")

    assert loss < maintenance
    assert gain > maintenance


def test_macros():
    result = calculate_macros(2300, 70)

    assert result["protein_g"] > 0
    assert result["fat_g"] > 0
    assert result["carbs_g"] > 0


def test_complete_profile():
    result = generate_nutrition_profile(
        age=20,
        weight_kg=70,
        height_cm=175,
        sex="male",
        activity_level="moderate",
        goal="weight_loss"
    )

    assert "bmr" in result
    assert "tdee" in result
    assert "calorie_target" in result
    assert "protein_g" in result
    assert "fat_g" in result
    assert "carbs_g" in result


def test_calculator():
    result = calculate_nutrition(
        20,
        70,
        175,
        "male",
        "moderate",
        "weight_loss"
    )

    assert result["bmr"] > 0
    assert result["tdee"] > 0
    assert result["calorie_target"] > 0