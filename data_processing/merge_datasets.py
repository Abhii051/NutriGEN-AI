from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path.cwd()

PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"

FOUNDATION_FILE = PROCESSED_FOLDER / "foundation_clean.csv"
SR_LEGACY_FILE = PROCESSED_FOLDER / "sr_legacy_clean.csv"

OUTPUT_FILE = PROCESSED_FOLDER / "master_food_dataset.csv"


print("=" * 70)
print("MERGING USDA DATASETS")
print("=" * 70)


# ------------------------------------------------------------
# Read datasets
# ------------------------------------------------------------

print("\nReading Foundation dataset...")
foundation = pd.read_csv(FOUNDATION_FILE)

print(f"Foundation records: {len(foundation):,}")


print("\nReading SR Legacy dataset...")
sr_legacy = pd.read_csv(SR_LEGACY_FILE)

print(f"SR Legacy records: {len(sr_legacy):,}")


# ------------------------------------------------------------
# Combine
# ------------------------------------------------------------

print("\nCombining datasets...")

master = pd.concat(
    [foundation, sr_legacy],
    ignore_index=True
)


# ------------------------------------------------------------
# Check duplicate USDA IDs
# ------------------------------------------------------------

duplicate_ids = master[
    master.duplicated(
        subset=["fdc_id"],
        keep=False
    )
]

print(
    f"\nDuplicate fdc_id records: "
    f"{len(duplicate_ids):,}"
)


# ------------------------------------------------------------
# Remove exact duplicate IDs
# ------------------------------------------------------------

master = master.drop_duplicates(
    subset=["fdc_id"],
    keep="first"
)


# ------------------------------------------------------------
# Sort by food name
# ------------------------------------------------------------

master = master.sort_values(
    by="description",
    na_position="last"
)


# ------------------------------------------------------------
# Reset index
# ------------------------------------------------------------

master = master.reset_index(drop=True)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

master.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n" + "=" * 70)
print("MERGE COMPLETE")
print("=" * 70)

print(f"\nFinal records: {len(master):,}")

print(f"\nSaved to:")
print(OUTPUT_FILE)


print("\nRecords by source:")
print(
    master["source_dataset"]
    .value_counts()
    .to_string()
)


print("\nFinal columns:")

for column in master.columns:
    print(" -", column)