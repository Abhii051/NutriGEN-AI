
import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

FOUNDATION_DIR = BASE_DIR / "data" / "raw" / "usda"
SR_LEGACY_DIR = BASE_DIR / "data" / "raw" / "usda_sr_legacy"

OUTPUT_DIR = BASE_DIR / "data" / "processed"

# Save as a NEW file to protect the existing dataset
OUTPUT_FILE = OUTPUT_DIR / "foods_combined_clean.csv"


# USDA nutrient IDs
PROTEIN_ID = 1003
FAT_ID = 1004
CARBS_ID = 1005
ENERGY_ID = 1008
ENERGY_GENERAL_ID = 2047
ENERGY_SPECIFIC_ID = 2048
FIBER_ID = 1079

REQUIRED_NUTRIENTS = [
    PROTEIN_ID,
    FAT_ID,
    CARBS_ID,
    ENERGY_ID,
    ENERGY_GENERAL_ID,
    ENERGY_SPECIFIC_ID,
    FIBER_ID,
]


def load_and_process_source(source_dir, source_name, data_type=None):
    """Load and process one USDA food dataset."""

    food_file = source_dir / "food.csv"
    nutrient_file = source_dir / "food_nutrient.csv"

    print(f"\nLoading {source_name}...")

    if not food_file.exists():
        raise FileNotFoundError(f"Missing file: {food_file}")

    if not nutrient_file.exists():
        raise FileNotFoundError(f"Missing file: {nutrient_file}")

    food = pd.read_csv(food_file, low_memory=False)
    food_nutrient = pd.read_csv(nutrient_file, low_memory=False)

    print(f"Food records loaded: {len(food)}")
    print(f"Nutrient records loaded: {len(food_nutrient)}")

    # Foundation Foods: keep Foundation Foods only.
    if data_type is not None:
        food = food[
            food["data_type"] == data_type
        ].copy()

    # Select the nutrients required by NutriGEN-AI
    food_nutrient = food_nutrient[
        food_nutrient["nutrient_id"].isin(
            REQUIRED_NUTRIENTS
        )
    ].copy()

    # Convert nutrient IDs into separate columns
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

    # Ensure all expected nutrient columns exist
    expected_columns = [
        "protein_g",
        "fat_g",
        "carbs_g",
        "fiber_g",
        "energy_1008",
        "energy_2047",
        "energy_2048",
    ]

    for column in expected_columns:
        if column not in nutrient_table.columns:
            nutrient_table[column] = pd.NA

    # Select the best available calorie value
    nutrient_table["calories"] = (
        nutrient_table["energy_1008"]
        .combine_first(nutrient_table["energy_2047"])
        .combine_first(nutrient_table["energy_2048"])
    )

    # Connect food records with nutrient information
    result = food[
        ["fdc_id", "description"]
    ].merge(
        nutrient_table,
        on="fdc_id",
        how="left"
    )

    # Rename columns
    result = result.rename(
        columns={
            "fdc_id": "food_id",
            "description": "food_name",
        }
    )

    # Add source information
    result["source"] = source_name

    nutrient_columns = [
        "calories",
        "protein_g",
        "carbs_g",
        "fat_g",
        "fiber_g",
    ]

    # Remove foods without calorie information
    result = result.dropna(
        subset=["calories"]
    )

    # Remove negative nutrient values.
    # Missing values are allowed; they are NOT treated as zero.
    for column in nutrient_columns:
        result = result[
            result[column].isna()
            | (result[column] >= 0)
        ]

    # Count available nutrition values
    result["nutrition_complete"] = (
        result[nutrient_columns].notna().sum(axis=1)
    )

    print(
        f"Usable records from {source_name}: "
        f"{len(result)}"
    )

    return result


def build_dataset():

    # Load Foundation Foods
    foundation = load_and_process_source(
        FOUNDATION_DIR,
        source_name="Foundation Foods",
        data_type="foundation_food"
    )

    # Load SR Legacy
    # The SR Legacy archive contains SR Legacy records,
    # so no Foundation Foods filter is applied.
    sr_legacy = load_and_process_source(
        SR_LEGACY_DIR,
        source_name="SR Legacy"
    )

    # Combine both datasets
    print("\nCombining datasets...")

    result = pd.concat(
        [foundation, sr_legacy],
        ignore_index=True
    )

    print(f"Records before deduplication: {len(result)}")

    # Normalize names temporarily for duplicate detection
    result["normalized_name"] = (
        result["food_name"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Prefer the record with more complete nutrition.
    # If tied, prefer Foundation Foods.
    result["source_priority"] = (
        result["source"].map({
            "Foundation Foods": 0,
            "SR Legacy": 1
        })
    )

    result = result.sort_values(
        by=[
            "normalized_name",
            "nutrition_complete",
            "source_priority"
        ],
        ascending=[True, False, True]
    )

    # Remove duplicate food names
    result = result.drop_duplicates(
        subset=["normalized_name"],
        keep="first"
    )

    # Remove temporary helper columns
    result = result.drop(
        columns=[
            "normalized_name",
            "nutrition_complete",
            "source_priority"
        ]
    )

    # Keep the final columns in a consistent order
    result = result[
        [
            "food_id",
            "food_name",
            "source",
            "protein_g",
            "fat_g",
            "carbs_g",
            "fiber_g",
            "calories"
        ]
    ]

    # Create output folder if needed
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save the combined dataset
    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nCombined dataset created successfully!")
    print(f"Final food records: {len(result)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nRecords by source:")
    print(result["source"].value_counts())

    print("\nFirst 10 foods:")
    print(result.head(10))


if __name__ == "__main__":
    build_dataset()