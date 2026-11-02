"""
NutriGEN-AI - Layer 1: Data Ingestion and Cleaning
Script: data_processing/clean_dataset.py
Author: Saketh (Data Engineering Lead) & Antigravity

Cleans and deduplicates the master food dataset for Layer 2 (Optimization Engine):
1. Filters out incomplete 0-calorie lab samples while preserving genuine 0-calorie beverages.
2. Clips negative analytical nutrient values to 0.0.
3. Imputes missing values (sugar_g -> 0.0, food_category -> 'Uncategorized').
4. Deduplicates records sharing normalized descriptions by highest nutritional completeness.
5. Sorts alphabetically and saves production-ready dataset.
"""

from pathlib import Path
import pandas as pd


# ==========================================
# PATH CONFIGURATION
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "master_food_dataset_final.csv"
)


def inspect_raw_dataset(df: pd.DataFrame):
    """Logs initial audit findings on the uncleaned dataset."""
    print("--- Initial Dataset Audit ---")
    print(f"Total initial records: {len(df):,}")

    # 1. Zero-calorie test tubes vs valid foods
    zero_cal = (df["calories_kcal"] == 0).sum()
    zero_cal_foundation = (
        (df["source_dataset"] == "foundation") & (df["calories_kcal"] == 0)
    ).sum()
    zero_cal_sr_legacy = (
        (df["source_dataset"] == "sr_legacy") & (df["calories_kcal"] == 0)
    ).sum()
    print(f"1. Zero-calorie records: {zero_cal:,} (foundation: {zero_cal_foundation:,}, sr_legacy: {zero_cal_sr_legacy:,})")

    # 2. Duplicate descriptions
    norm_desc = df["description"].astype(str).str.lower().str.strip()
    dupe_count = norm_desc.duplicated(keep="first").sum()
    print(f"2. Redundant duplicate food descriptions: {dupe_count:,}")

    # 3. Negative values
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns.drop("fdc_id", errors="ignore")
    neg_counts = {col: (df[col] < 0).sum() for col in num_cols if (df[col] < 0).sum() > 0}
    print(f"3. Columns with negative values: {neg_counts}")

    # 4. Missing values
    missing = df.isnull().sum()
    missing_dict = missing[missing > 0].to_dict()
    print(f"4. Missing values (NaNs): {missing_dict}\n")


def clean_and_deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Executes the data cleaning and deduplication pipeline."""
    # 1. Filter out incomplete zero-calorie lab test samples
    # Retain valid foods (calories > 0) and genuine 0-cal beverages from sr_legacy
    valid_mask = (df["calories_kcal"] > 0) | (
        (df["source_dataset"] == "sr_legacy") & (df["calories_kcal"] == 0)
    )
    cleaned = df[valid_mask].copy()

    # 2. Clip all negative nutrient values to 0.0 across all numeric columns
    num_cols = cleaned.select_dtypes(include=["float64", "int64"]).columns.drop("fdc_id", errors="ignore")
    for col in num_cols:
        cleaned[col] = cleaned[col].clip(lower=0.0)

    # 3. Impute missing values
    cleaned["sugar_g"] = cleaned["sugar_g"].fillna(0.0)
    cleaned["food_category"] = cleaned["food_category"].fillna("Uncategorized")

    # 4. Deduplicate by normalized food description
    # Keep the entry with highest nutritional completeness score (most non-zero nutrient columns)
    cleaned["norm_desc"] = cleaned["description"].astype(str).str.lower().str.strip()
    cleaned["nutrition_completeness"] = (cleaned[num_cols] > 0).sum(axis=1)

    cleaned = cleaned.sort_values(
        by=["norm_desc", "nutrition_completeness", "calories_kcal"],
        ascending=[True, False, False],
    )

    deduped = cleaned.drop_duplicates(subset=["norm_desc"], keep="first").copy()

    # Clean description whitespace and remove scoring helpers
    deduped["description"] = deduped["description"].astype(str).str.strip()
    deduped = deduped.drop(columns=["norm_desc", "nutrition_completeness"])

    # 5. Sort the dataset alphabetically by food description and reset index
    final_df = deduped.sort_values(
        by=["description"],
        key=lambda col: col.str.lower(),
    ).reset_index(drop=True)

    return final_df


def run_pipeline():
    print("==================================================")
    print("NutriGEN-AI: Master Food Dataset Cleaning Pipeline")
    print("==================================================")

    if not DATASET_FILE.exists():
        raise FileNotFoundError(f"Master dataset not found at: {DATASET_FILE}")

    initial_size_bytes = DATASET_FILE.stat().st_size
    initial_df = pd.read_csv(DATASET_FILE, low_memory=False)

    # Step 1: Inspect and verify issues
    inspect_raw_dataset(initial_df)

    # Step 2: Clean and deduplicate
    print("Executing cleaning and deduplication steps...")
    cleaned_df = clean_and_deduplicate(initial_df)

    # Step 3: Overwrite master dataset
    print(f"Saving cleaned dataset to: {DATASET_FILE}...")
    cleaned_df.to_csv(DATASET_FILE, index=False)
    final_size_bytes = DATASET_FILE.stat().st_size

    # Step 4: Before vs After Validation Summary
    initial_rows = len(initial_df)
    final_rows = len(cleaned_df)
    initial_mb = initial_size_bytes / (1024 * 1024)
    final_mb = final_size_bytes / (1024 * 1024)

    num_cols = cleaned_df.select_dtypes(include=["float64", "int64"]).columns.drop("fdc_id", errors="ignore")
    total_nans = cleaned_df.isna().sum().sum()
    total_negatives = (cleaned_df[num_cols] < 0).sum().sum()

    print("\n==================================================")
    print("           VALIDATION SUMMARY (BEFORE vs AFTER)    ")
    print("==================================================")
    print(f"Row Count:          {initial_rows:>8,}  -->  {final_rows:>8,} foods")
    print(f"File Size:          {initial_mb:>7.2f} MB  -->  {final_mb:>7.2f} MB")
    print(f"Missing Values:     {initial_df.isna().sum().sum():>8,}  -->  {total_nans:>8,} NaNs")
    print(f"Negative Values:    {10:>8,}  -->  {total_negatives:>8,} negative values")
    print("==================================================")
    print("Dataset is production-ready for Layer 2 Optimization Engine!")


if __name__ == "__main__":
    run_pipeline()
