import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from Backend.src.preferences import (
    create_preferences,
    apply_preferences,
)

from Backend.src.candidates import (
    select_candidate_pool,
)


DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_food_dataset_final.csv"
)


def main():

    print("Loading dataset...")

    df = pd.read_csv(
        DATASET_PATH,
        low_memory=False
    )

    print("Original foods:", len(df))

    preferences = create_preferences(
        diet_type="vegetarian",
        eats_eggs=True,
        cuisine="indian",
        allergies=["peanut"],
        disliked_foods=["mushroom"],
        number_of_meals=3,
        number_of_snacks=1,
    )

    filtered_df = apply_preferences(
        df,
        preferences
    )

    print("After preferences:", len(filtered_df))

    candidate_pool = select_candidate_pool(
        filtered_df,
        max_per_role=100
    )

    print("Candidate pool:", len(candidate_pool))

    print("\n===== FOOD ROLES =====")

    print(
        candidate_pool["food_role"]
        .value_counts()
        .to_string()
    )

    print("\n===== SAMPLE CANDIDATES =====")

    columns = [
        "description",
        "food_role",
        "cuisine_score"
    ]

    print(
        candidate_pool[columns]
        .head(50)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()