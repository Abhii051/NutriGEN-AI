from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_food_dataset_classified.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_food_dataset_final.csv"
)


df = pd.read_csv(INPUT_FILE)

print(f"Original records: {len(df):,}")


# ---------------------------------------------------------
# Remove records without a food description
# ---------------------------------------------------------

missing_description = df["description"].isna()

removed_count = missing_description.sum()

df = df[~missing_description].copy()


print(
    f"Removed records without description: "
    f"{removed_count:,}"
)

print(f"Final records: {len(df):,}")


# ---------------------------------------------------------
# Save final dataset
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nFinal dataset saved to:")
print(OUTPUT_FILE) 