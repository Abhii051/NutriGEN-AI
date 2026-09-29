import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "foods_classified_v2.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "v2_suggestions_for_review.csv"
)

df = pd.read_csv(INPUT_FILE)

# Only show foods that were previously unknown
# but received a new keyword-based suggestion.
suggestions = df[
    df["classification_method"]
    == "keyword_suggestion_unverified"
].copy()

print("New suggestions:", len(suggestions))
print("\nSuggested label counts:")
print(suggestions["food_type_v2"].value_counts())

print("\nSample suggestions:\n")

for label in [
    "vegan",
    "non_vegetarian"
]:
    subset = suggestions[
        suggestions["food_type_v2"] == label
    ]

    print(f"\n--- {label.upper()} ---")

    for name in subset["food_name"].head(50):
        print("-", name)

suggestions[
    [
        "food_id",
        "food_name",
        "food_type",
        "food_type_v2",
        "classification_method"
    ]
].to_csv(OUTPUT_FILE, index=False)

print("\nReview file saved to:")
print(OUTPUT_FILE)