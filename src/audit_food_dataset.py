
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "foods_combined_classified_reviewed.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. LOAD DATA
# ==========================================

print("Loading food dataset...")

df = pd.read_csv(INPUT_FILE)

print("Total records:", len(df))
print("Total columns:", len(df.columns))

print("\nColumns found:")
print(df.columns.tolist())

# ==========================================
# 3. CHECK REQUIRED COLUMNS
# ==========================================

# Support either common naming convention.
name_col = next(
    (c for c in ["food_name", "description", "food_description"]
     if c in df.columns),
    None
)

label_col = next(
    (c for c in ["food_type", "food_category", "category"]
     if c in df.columns),
    None
)

if name_col is None:
    raise ValueError(
        "Food name column not found. "
        "Check the printed column names."
    )

if label_col is None:
    raise ValueError(
        "Food category column not found. "
        "Check the printed column names."
    )

# Nutrition columns that may exist in this dataset.
nutrition_candidates = [
    "calories", "calories_kcal",
    "protein_g", "fat_g",
    "carbs_g", "carbohydrate_g",
    "fiber_g", "sugar_g",
    "calcium_mg", "iron_mg",
    "magnesium_mg", "potassium_mg",
    "sodium_mg", "zinc_mg",
    "vitamin_a_ug", "vitamin_e_mg",
    "vitamin_d_ug"
]

nutrition_cols = [
    c for c in nutrition_candidates if c in df.columns
]

# ==========================================
# 4. MISSING VALUES
# ==========================================

print("\n========== MISSING VALUES ==========")

missing = df.isna().sum()

missing_report = pd.DataFrame({
    "column": missing.index,
    "missing_count": missing.values,
    "missing_percent": (
        missing.values / len(df) * 100
    ).round(2)
})

missing_report = missing_report.sort_values(
    "missing_count", ascending=False
)

print(missing_report.to_string(index=False))

missing_report.to_csv(
    OUTPUT_DIR / "audit_missing_values.csv",
    index=False
)

# ==========================================
# 5. DUPLICATE CHECK
# ==========================================

print("\n========== DUPLICATES ==========")

full_duplicates = df.duplicated().sum()

print("Exact duplicate rows:", full_duplicates)

# Duplicate food names are candidates for review,
# not automatically errors. Different food forms
# can legitimately share similar names.

duplicate_names = df[
    df[name_col].notna()
    & df[name_col].astype(str).str.strip().ne("")
    & df[name_col].astype(str).str.strip().str.lower().duplicated(
        keep=False
    )
].sort_values(name_col)

print("Rows with repeated food names:", len(duplicate_names))

duplicate_names.to_csv(
    OUTPUT_DIR / "audit_duplicate_food_names.csv",
    index=False
)

# ==========================================
# 6. EMPTY FOOD NAMES
# ==========================================

print("\n========== FOOD NAMES ==========")

empty_names = (
    df[name_col].isna()
    | df[name_col].astype(str).str.strip().eq("")
)

print("Empty food names:", empty_names.sum())

empty_name_rows = df[empty_names]

empty_name_rows.to_csv(
    OUTPUT_DIR / "audit_empty_food_names.csv",
    index=False
)

# ==========================================
# 7. FOOD LABEL CHECK
# ==========================================

print("\n========== FOOD LABELS ==========")

df[label_col] = df[label_col].astype("string").str.strip().str.lower()

valid_labels = [
    "vegan",
    "vegetarian",
    "non_vegetarian"
]

unknown_values = df[
    df[label_col].isna()
    | ~df[label_col].isin(valid_labels)
]

print("\nLabel counts:")
print(df[label_col].value_counts(dropna=False))

print("\nRows with missing or unrecognized labels:",
      len(unknown_values))

unknown_values.to_csv(
    OUTPUT_DIR / "audit_unknown_food_labels.csv",
    index=False
)

# ==========================================
# 8. NUTRITION VALUE CHECK
# ==========================================

print("\n========== NUTRITION CHECK ==========")

for col in nutrition_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

    missing_count = df[col].isna().sum()
    negative_count = (df[col] < 0).sum()

    print(
        f"{col}: missing={missing_count}, "
        f"negative={negative_count}"
    )

# Negative nutrient values are flagged for review.
# Zero values are NOT automatically considered errors.

negative_mask = pd.Series(False, index=df.index)

for col in nutrition_cols:
    negative_mask |= df[col] < 0

negative_rows = df[negative_mask]

negative_rows.to_csv(
    OUTPUT_DIR / "audit_negative_nutrition.csv",
    index=False
)

# ==========================================
# 9. ALL-ZERO NUTRITION CHECK
# ==========================================

print("\n========== ZERO NUTRITION CHECK ==========")

if nutrition_cols:
    all_zero_mask = (
        df[nutrition_cols].fillna(0).eq(0).all(axis=1)
    )

    all_zero_rows = df[all_zero_mask]

    print(
        "Records with all available nutrition "
        "values zero or missing:",
        len(all_zero_rows)
    )

    all_zero_rows.to_csv(
        OUTPUT_DIR / "audit_all_zero_nutrition.csv",
        index=False
    )
else:
    print("No recognized nutrition columns found.")

# ==========================================
# 10. FINAL SUMMARY
# ==========================================

print("\n========== AUDIT SUMMARY ==========")

print("Total records:", len(df))
print("Exact duplicate rows:", full_duplicates)
print("Empty food names:", empty_names.sum())
print("Unknown/missing food labels:", len(unknown_values))
print("Negative nutrition records:", len(negative_rows))

print("\nAudit reports saved in:")
print(OUTPUT_DIR)

print("\nAudit completed.")