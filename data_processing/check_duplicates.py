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

# ---------------------------------------------------------
# 1. Exact FDC ID duplicates
# ---------------------------------------------------------

fdc_duplicates = df["fdc_id"].duplicated().sum()

print(f"\nDuplicate fdc_id records: {fdc_duplicates:,}")


# ---------------------------------------------------------
# 2. Exact description duplicates
# ---------------------------------------------------------

description_duplicates = df["description"].duplicated().sum()

print(
    f"Duplicate descriptions: "
    f"{description_duplicates:,}"
)


# ---------------------------------------------------------
# 3. Normalized description duplicates
# ---------------------------------------------------------

df["normalized_description"] = (
    df["description"]
    .astype(str)
    .str.lower()
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

normalized_duplicates = (
    df["normalized_description"].duplicated().sum()
)

print(
    f"Normalized description duplicates: "
    f"{normalized_duplicates:,}"
)


# ---------------------------------------------------------
# 4. Show common duplicate descriptions
# ---------------------------------------------------------

duplicate_rows = (
    df[df["normalized_description"].duplicated(keep=False)]
    .sort_values("normalized_description")
)

print("\nSample duplicate descriptions:")

print(
    duplicate_rows[
        [
            "fdc_id",
            "source_dataset",
            "description",
            "food_category",
            "diet_type"
        ]
    ]
    .head(50)
    .to_string(index=False)
)
