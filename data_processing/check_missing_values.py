from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_food_dataset_classified.csv"
)

df = pd.read_csv(INPUT_FILE)

print(f"Total records: {len(df):,}")
print("\nMissing values by column:")
print(df.isna().sum().sort_values(ascending=False))


print("\nMissing percentage by column:")
missing_percent = (
    df.isna().mean() * 100
).sort_values(ascending=False)

print(missing_percent.round(2))