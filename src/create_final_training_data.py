
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "foods_classified_v2.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

df = pd.read_csv(INPUT_FILE)

# Use only the original, known labels.
valid_labels = [
    "vegan",
    "vegetarian",
    "non_vegetarian"
]

training_df = df[
    df["food_type"].isin(valid_labels)
].copy()

# Keep the original food_type as the training target.
training_df["food_type_final"] = training_df["food_type"]

# Remove unverified suggestions from training.
training_df = training_df.drop(
    columns=["food_type_v2", "classification_method"],
    errors="ignore"
)

# Save final training data.
training_file = OUTPUT_DIR / "foods_final_training.csv"
training_df.to_csv(training_file, index=False)

# Save all remaining records for future review.
unknown_df = df[
    df["food_type"] == "unknown"
].copy()

unknown_file = OUTPUT_DIR / "foods_unresolved.csv"
unknown_df.to_csv(unknown_file, index=False)

print("Total master records:", len(df))
print("Training records:", len(training_df))
print("\nTraining label counts:")
print(training_df["food_type_final"].value_counts())

print("\nUnresolved original records:", len(unknown_df))

print("\nTraining dataset saved to:")
print(training_file)

print("\nUnresolved dataset saved to:")
print(unknown_file)