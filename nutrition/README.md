# NutriGEN-AI
Personalized Meal Plan Generator
# NutriGEN-AI Nutrition Module

## Purpose

This module calculates a user's basic daily nutrition requirements based on their personal inputs, activity level, and goal.

## Inputs

- Age
- Weight (kg)
- Height (cm)
- Sex
- Activity level
- Goal

### Activity Levels

- `sedentary`
- `light`
- `moderate`
- `very_active`
- `extremely_active`

### Goals

- `weight_loss`
- `maintenance`
- `weight_gain`

## Calculations

The module calculates:

1. BMR (Basal Metabolic Rate)
2. TDEE (Total Daily Energy Expenditure)
3. Daily calorie target
4. Protein target
5. Fat target
6. Carbohydrate target

## Main Files

### `ai_model.py`

Contains the core nutrition calculation functions:

- `calculate_bmr()`
- `calculate_tdee()`
- `calculate_calorie_target()`
- `calculate_macros()`
- `generate_nutrition_profile()`

### `nutrition/src/calculator.py`

Provides a simple interface for accepting user information and calling the nutrition model.

### `nutrition/tests/test_nutrition.py`

Contains automated tests for the nutrition calculation functions and calculator interface.

## Output

The nutrition profile is returned as a Python dictionary containing:

- `bmr`
- `tdee`
- `calorie_target`
- `protein_g`
- `fat_g`
- `carbs_g`

## Testing

Run the tests from the project root:

```bash
python3 -m pytest nutrition/tests/test_nutrition.py
```

Current test status: **6 tests passed.**

## Note

The calorie and macronutrient targets currently use prototype assumptions for software development and testing. They should not be treated as individualized medical or dietary advice.