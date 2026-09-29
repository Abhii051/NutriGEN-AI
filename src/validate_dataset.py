import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "foods_combined_classified_reviewed.csv"

def validate_dataset():

    print("Loading classified dataset...")

    df = pd.read_csv(INPUT_FILE)

    # Required columns
    required_columns = [
        "food_id",
        "food_name",
        "protein_g",
        "carbs_g",
        "fat_g",
        "fiber_g",
        "calories",
        "food_type",
    ]

    print("\nChecking required columns...")

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing column: {column}")

    print("All required columns are present.")

    # Check missing values
    print("\nChecking missing values...")

    print(df[required_columns].isnull().sum())

    # Check duplicate IDs
    print("\nDuplicate food IDs:")
    print(df["food_id"].duplicated().sum())

    # Check duplicate names
    print("\nDuplicate food names:")
    print(df["food_name"].duplicated().sum())

    # Check category counts
    print("\nFood category counts:")
    print(df["food_type"].value_counts())

    # Check invalid categories
    valid_categories = [
        "vegan",
        "vegetarian",
        "non_vegetarian",
        "unknown",
    ]

    invalid = df[~df["food_type"].isin(valid_categories)]

    print("\nInvalid food categories:")
    print(len(invalid))

    # Check negative nutritional values
    nutrition_columns = [
        "calories",
        "protein_g",
        "carbs_g",
        "fat_g",
        "fiber_g",
    ]

    print("\nNegative nutritional values:")

    for column in nutrition_columns:
        print(
            column,
            (df[column] < 0).sum()
        )

    # Final summary
    print("\nTotal food records:", len(df))

    print("\nValidation checks completed!")


if __name__ == "__main__":
    validate_dataset()