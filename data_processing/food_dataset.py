from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path.cwd()

DATASETS = {
    "foundation": PROJECT_ROOT / "data" / "raw" / "foundation",
    "sr_legacy": PROJECT_ROOT / "data" / "raw" / "sr_legacy",
}

OUTPUT_FOLDER = PROJECT_ROOT / "data" / "processed"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# NUTRIENTS WE WANT
# ============================================================

NUTRIENTS = {
    1008: "calories_kcal",
    1003: "protein_g",
    1004: "fat_g",
    1005: "carbohydrate_g",
    1079: "fiber_g",
    1063: "sugar_g",
    1087: "calcium_mg",
    1089: "iron_mg",
    1090: "magnesium_mg",
    1091: "phosphorus_mg",
    1092: "potassium_mg",
    1093: "sodium_mg",
    1095: "zinc_mg",
    1106: "vitamin_a_ug",
    1109: "vitamin_e_mg",
    1114: "vitamin_d_ug",
    1162: "vitamin_c_mg",
    1165: "thiamin_b1_mg",
    1166: "riboflavin_b2_mg",
    1167: "niacin_b3_mg",
    1177: "folate_ug",
    1178: "vitamin_b12_ug",
    1185: "vitamin_k_ug",
}


# ============================================================
# FIND USDA FILE
# ============================================================

def find_file(root_folder, filename):
    matches = list(root_folder.rglob(filename))

    if not matches:
        raise FileNotFoundError(
            f"Could not find {filename} inside {root_folder}"
        )

    if len(matches) > 1:
        print(f"WARNING: Multiple {filename} files found:")
        for match in matches:
            print("  ", match)

    return matches[0]


# ============================================================
# BUILD ONE DATASET
# ============================================================

def build_dataset(dataset_name, dataset_folder):

    print("\n" + "=" * 70)
    print(f"BUILDING: {dataset_name.upper()}")
    print("=" * 70)

    # --------------------------------------------------------
    # Locate files
    # --------------------------------------------------------

    food_file = find_file(dataset_folder, "food.csv")
    nutrient_file = find_file(dataset_folder, "food_nutrient.csv")
    category_file = find_file(dataset_folder, "food_category.csv")

    print("\nReading files...")

    # --------------------------------------------------------
    # Read food table
    # --------------------------------------------------------

    food = pd.read_csv(food_file)

    print(f"Food records: {len(food):,}")

    # --------------------------------------------------------
    # Read category table
    # --------------------------------------------------------

    categories = pd.read_csv(category_file)

    categories = categories.rename(
        columns={
            "id": "food_category_id",
            "description": "food_category"
        }
    )

    categories = categories[
        ["food_category_id", "food_category"]
    ]

    # --------------------------------------------------------
    # Attach category names
    # --------------------------------------------------------

    food = food.merge(
        categories,
        on="food_category_id",
        how="left"
    )

    # --------------------------------------------------------
    # Read nutrient table
    # --------------------------------------------------------

    food_nutrients = pd.read_csv(nutrient_file)

    print(f"Nutrient records: {len(food_nutrients):,}")

    # --------------------------------------------------------
    # Keep only required nutrients
    # --------------------------------------------------------

    food_nutrients = food_nutrients[
        food_nutrients["nutrient_id"].isin(NUTRIENTS.keys())
    ].copy()

    print(
        f"Selected nutrient records: "
        f"{len(food_nutrients):,}"
    )

    # --------------------------------------------------------
    # Convert nutrient IDs into readable column names
    # --------------------------------------------------------

    food_nutrients["nutrient_name"] = (
        food_nutrients["nutrient_id"]
        .map(NUTRIENTS)
    )

    # --------------------------------------------------------
    # Keep only necessary columns
    # --------------------------------------------------------

    food_nutrients = food_nutrients[
        ["fdc_id", "nutrient_name", "amount"]
    ]

    # --------------------------------------------------------
    # Pivot nutrients
    # --------------------------------------------------------

    nutrients_pivot = food_nutrients.pivot_table(
        index="fdc_id",
        columns="nutrient_name",
        values="amount",
        aggfunc="first"
    ).reset_index()

    # Remove pivot column name
    nutrients_pivot.columns.name = None

    # --------------------------------------------------------
    # Merge nutrition values with food information
    # --------------------------------------------------------

    final_df = food.merge(
        nutrients_pivot,
        on="fdc_id",
        how="left"
    )

    # --------------------------------------------------------
    # Add source
    # --------------------------------------------------------

    final_df["source_dataset"] = dataset_name

    # --------------------------------------------------------
    # Select final columns
    # --------------------------------------------------------

    base_columns = [
        "fdc_id",
        "source_dataset",
        "description",
        "food_category",
        "publication_date",
    ]

    nutrient_columns = list(NUTRIENTS.values())

    final_columns = base_columns + nutrient_columns

    # Only keep columns that actually exist
    final_columns = [
        column
        for column in final_columns
        if column in final_df.columns
    ]

    final_df = final_df[final_columns]

    # --------------------------------------------------------
    # Replace missing nutrition values with 0
    # --------------------------------------------------------

    for column in nutrient_columns:
        if column in final_df.columns:
            final_df[column] = final_df[column].fillna(0)

    # --------------------------------------------------------
    # Remove duplicate fdc_id records
    # --------------------------------------------------------

    before = len(final_df)

    final_df = final_df.drop_duplicates(
        subset=["fdc_id"]
    )

    after = len(final_df)

    print(
        f"Removed {before - after:,} duplicate "
        f"fdc_id records."
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_file = (
        OUTPUT_FOLDER /
        f"{dataset_name}_clean.csv"
    )

    final_df.to_csv(
        output_file,
        index=False
    )

    print(f"\nSaved: {output_file}")
    print(f"Final records: {len(final_df):,}")

    print("\nColumns:")
    for column in final_df.columns:
        print(" -", column)

    return final_df


# ============================================================
# MAIN
# ============================================================

def main():

    for dataset_name, dataset_folder in DATASETS.items():

        build_dataset(
            dataset_name,
            dataset_folder
        )

    print("\n" + "=" * 70)
    print("DATASET BUILD COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()