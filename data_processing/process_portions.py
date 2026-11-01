import pandas as pd
from pathlib import Path

# Paths
portion_file = Path(
    "data/raw/foundation/"
    "FoodData_Central_foundation_food_csv_2026-04-30/"
    "food_portion.csv"
)

output_file = Path("data/processed/food_portions.csv")

# Load USDA portion data
df = pd.read_csv(portion_file)

# Keep useful columns
columns = [
    "fdc_id",
    "amount",
    "measure_unit_id",
    "portion_description",
    "modifier",
    "gram_weight"
]

df = df[columns].copy()

# Remove rows without a valid food ID or gram weight
df = df.dropna(subset=["fdc_id", "gram_weight"])

# Make IDs consistent
df["fdc_id"] = df["fdc_id"].astype(int)

# Remove exact duplicate portion records
df = df.drop_duplicates()

# Sort for easier inspection
df = df.sort_values(["fdc_id", "gram_weight"])

# Save
df.to_csv(output_file, index=False)

print("===== PORTION DATASET =====")
print("Portion records:", len(df))
print("Unique foods:", df["fdc_id"].nunique())
print("Missing gram weights:", df["gram_weight"].isna().sum())
print("Saved to:", output_file)
