import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

FOOD_FILE = BASE_DIR / "data" / "raw" / "usda" / "food.csv"
FOOD_NUTRIENT_FILE = BASE_DIR / "data" / "raw" / "usda" / "food_nutrient.csv"

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "foods_clean.csv"


# USDA nutrient IDs
PROTEIN_ID = 1003
FAT_ID = 1004
CARBS_ID = 1005
ENERGY_ID = 1008
ENERGY_GENERAL_ID = 2047
ENERGY_SPECIFIC_ID = 2048
FIBER_ID = 1079


def build_dataset():
    print("Loading USDA food data...")

    food = pd.read_csv(FOOD_FILE)
    food_nutrient = pd.read_csv(FOOD_NUTRIENT_FILE)

    print(f"Food records loaded: {len(food)}")
    print(f"Nutrient records loaded: {len(food_nutrient)}")

    # Keep Foundation Foods only
    food = food[food["data_type"] == "foundation_food"].copy()

    # Keep only the nutrients required by NutriGEN-AI
    required_nutrients = [
        PROTEIN_ID,
        FAT_ID,
        CARBS_ID,
        ENERGY_ID,
        ENERGY_GENERAL_ID,
        ENERGY_SPECIFIC_ID,
        FIBER_ID,
    ]

    food_nutrient = food_nutrient[
        food_nutrient["nutrient_id"].isin(required_nutrients)
    ].copy()

    # Convert nutrient rows into columns
    nutrient_table = food_nutrient.pivot_table(
        index="fdc_id",
        columns="nutrient_id",
        values="amount",
        aggfunc="mean"
    ).reset_index()

    # Rename nutrient columns
    nutrient_table = nutrient_table.rename(
        columns={
            PROTEIN_ID: "protein_g",
            FAT_ID: "fat_g",
            CARBS_ID: "carbs_g",
            ENERGY_ID: "energy_1008",
            ENERGY_GENERAL_ID: "energy_2047",
            ENERGY_SPECIFIC_ID: "energy_2048",
            FIBER_ID: "fiber_g",
        }
    )

    # Select the best available calorie value.
    # Priority:
    # Energy (1008) -> Atwater General (2047) -> Atwater Specific (2048)
    nutrient_table["calories"] = (
        nutrient_table["energy_1008"]
        .combine_first(nutrient_table["energy_2047"])
        .combine_first(nutrient_table["energy_2048"])
    )

    # Remove temporary energy columns
    nutrient_table = nutrient_table.drop(
        columns=[
            "energy_1008",
            "energy_2047",
            "energy_2048"
        ]
    )

    # Connect food information with nutrient information
    result = food[
        ["fdc_id", "description"]
    ].merge(
        nutrient_table,
        on="fdc_id",
        how="left"
    )

    # Rename columns for our project
    result = result.rename(
        columns={
            "fdc_id": "food_id",
            "description": "food_name",
        }
    )

    # Nutrients required by NutriGEN-AI
    nutrient_columns = [
        "calories",
        "protein_g",
        "carbs_g",
        "fat_g",
        "fiber_g",
    ]

    # Remove foods without any nutrition information
    result = result.dropna(
        subset=nutrient_columns,
        how="all"
    )

    # Calories are essential for meal-plan optimization.
    # Do NOT treat missing calories as 0.
    result = result.dropna(
        subset=["calories"]
    )

    # Remove impossible negative values
    for column in nutrient_columns:
        result = result[result[column] >= 0]

    # Prefer food records with more complete nutrition information
    result["nutrition_complete"] = (
        result[nutrient_columns] != 0
    ).sum(axis=1)

    # Remove duplicate food names.
    # When duplicates exist, keep the record with more nutrition values.
    result = result.sort_values(
        by=["food_name", "nutrition_complete"],
        ascending=[True, False]
    )

    result = result.drop_duplicates(
        subset=["food_name"],
        keep="first"
    )

    # Remove helper column
    result = result.drop(
        columns=["nutrition_complete"]
    )

    # Create processed directory if it doesn't exist
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save final dataset
    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nDataset created successfully!")
    print(f"Final food records: {len(result)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nColumns:")
    print(list(result.columns))

    print("\nFirst 10 foods:")
    print(result.head(10))


if __name__ == "__main__":
    build_dataset()