import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from Backend.src.preferences import (
    create_preferences,
    apply_preferences,
)


DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_food_dataset_final.csv"
)


def main():

    print("Loading dataset...")

    df = __import__("pandas").read_csv(
        DATASET_PATH,
        low_memory=False
    )

    print("Original foods:", len(df))

    preferences = create_preferences(
        diet_type="vegetarian",
        eats_eggs=True,
        cuisine="indian",
        allergies=["peanuts"],
        disliked_foods=["mushroom"],
        number_of_meals=3,
        number_of_snacks=1,
    )

    filtered_df = apply_preferences(
        df,
        preferences
    )

    print(
        "Foods after filtering:",
        len(filtered_df)
    )

    print("\n===== SAMPLE FOODS =====")

    columns = [
        "description",
        "diet_type",
        "cuisine_score",
    ]

    available_columns = [
        col for col in columns
        if col in filtered_df.columns
    ]

    print(
        filtered_df[
            available_columns
        ].head(20).to_string(index=False)
    )

    print("\n===== CUISINE SCORE =====")

    print(
        filtered_df["cuisine_score"]
        .value_counts()
        .to_string()
    )


if __name__ == "__main__":
    main()