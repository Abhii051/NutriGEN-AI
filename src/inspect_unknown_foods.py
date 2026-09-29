
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "unknown_foods_suggestions.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

df = pd.read_csv(INPUT_FILE)

# Foods for which the keyword script found no suggestion
remaining = df[
    df["suggested_food_type"] == "needs_manual_review"
].copy()

print("Foods needing manual review:", len(remaining))

# Save a smaller file for convenient review
review_file = OUTPUT_DIR / "unknown_foods_names_for_review.csv"

remaining[
    ["food_id", "food_name", "source", "food_type",
     "suggested_food_type"]
].to_csv(review_file, index=False)

print("\nFirst 100 food names:\n")

for i, name in enumerate(remaining["food_name"].head(100), 1):
    print(f"{i}. {name}")

print("\nReview file saved to:")
print(review_file)