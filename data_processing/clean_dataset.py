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


def run_pipeline():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print(f"Original records: {len(df):,}")

    # Remove records without a food description
    missing_description = df["description"].isna()
    removed = missing_description.sum()
    df = df.loc[~missing_description].copy()

    print(f"Removed missing descriptions: {removed:,}")

    # Clip negative nutritional values without changing missing values
    numeric_cols = df.select_dtypes(include="number").columns
    numeric_cols = numeric_cols.drop("fdc_id", errors="ignore")

    for col in numeric_cols:
        df[col] = df[col].clip(lower=0)

    # Remove only completely identical rows
    before = len(df)
    df = df.drop_duplicates()
    print(f"Removed exact duplicate rows: {before - len(df):,}")

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Final records: {len(df):,}")
    print(f"Final dataset saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_pipeline()
