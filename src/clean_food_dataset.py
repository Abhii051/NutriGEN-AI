
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "foods_combined_classified_reviewed.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_FILE = OUTPUT_DIR / "foods_final_cleaned.csv"

REVIEW_FILE = OUTPUT_DIR / "foods_needing_review.csv"

NUTRITION_REVIEW_FILE = (
    OUTPUT_DIR / "foods_missing_or_zero_nutrition.csv"
)

# ==========================================
# 2. LOAD DATA
# ==========================================

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE)

original_count = len(df)

print("Original records:", original_count)

# ==========================================
# 3. CLEAN FOOD NAMES AND LABELS
# ==========================================

df["food_name"] = (
    df["food_name"]
    .astype("string")
    .str.strip()
)

df["food_type"] = (
    df["food_type"]
    .astype("string")
    .str.strip()
    .str.lower()
)

# ==========================================
# 4. CONVERT NUTRITION TO NUMERIC
# ==========================================

nutrition_columns = [
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "fiber_g"
]

for col in nutrition_columns:
    df[col] = pd.to_numeric(
        df[col], errors="coerce"
    )

# ==========================================
# 5. REMOVE EXACT DUPLICATES
# ==========================================

before_duplicates = len(df)

df = df.drop_duplicates().copy()

duplicates_removed = before_duplicates - len(df)

print("Exact duplicate rows removed:", duplicates_removed)

# ==========================================
# 6. FLAG MISSING NUTRITION
# ==========================================

# Missing values remain missing.
# We do not invent nutrition values.

df["nutrition_needs_review"] = (
    df[nutrition_columns].isna().any(axis=1)
)

# ==========================================
# 7. FLAG ALL-ZERO NUTRITION
# ==========================================

df["all_nutrition_zero_or_missing"] = (
    df[nutrition_columns].fillna(0).eq(0).all(axis=1)
)

# ==========================================
# 8. FLAG UNKNOWN FOOD TYPES
# ==========================================

valid_labels = [
    "vegan",
    "vegetarian",
    "non_vegetarian"
]

df["food_type_needs_review"] = (
    df["food_type"].isna()
    | ~df["food_type"].isin(valid_labels)
)

# ==========================================
# 9. GENERATE REVIEW FILES
# ==========================================

review_mask = (
    df["food_type_needs_review"]
    | df["nutrition_needs_review"]
    | df["all_nutrition_zero_or_missing"]
)

review_df = df[review_mask].copy()

review_df.to_csv(REVIEW_FILE, index=False)

nutrition_review_df = df[
    df["nutrition_needs_review"]
    | df["all_nutrition_zero_or_missing"]
].copy()

nutrition_review_df.to_csv(
    NUTRITION_REVIEW_FILE,
    index=False
)

# ==========================================
# 10. SAVE CLEANED DATASET
# ==========================================

df.to_csv(CLEAN_FILE, index=False)

# ==========================================
# 11. SUMMARY
# ==========================================

print("\n========== CLEANING SUMMARY ==========")

print("Original records:", original_count)
print("Final records:", len(df))

print(
    "Records needing label review:",
    int(df["food_type_needs_review"].sum())
)

print(
    "Records needing nutrition review:",
    int(df["nutrition_needs_review"].sum())
)

print(
    "Records with all nutrition zero or missing:",
    int(df["all_nutrition_zero_or_missing"].sum())
)

print("\nFinal label counts:")
print(df["food_type"].value_counts(dropna=False))

print("\nCleaned dataset saved to:")
print(CLEAN_FILE)

print("\nReview files saved:")
print(REVIEW_FILE)
print(NUTRITION_REVIEW_FILE)

print("\nCleaning completed.")