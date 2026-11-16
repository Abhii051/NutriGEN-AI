from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path.cwd()

DATASETS = {
    "Foundation": PROJECT_ROOT / "data" / "raw" / "foundation",
    "SR Legacy": PROJECT_ROOT / "data" / "raw" / "sr_legacy",
}


# Nutrients important for NutriGEN-AI
SEARCH_TERMS = [
    "Energy",
    "Protein",
    "Carbohydrate",
    "Total lipid",
    "Fat",
    "Fiber",
    "Sugars",
    "Sodium",
    "Potassium",
    "Calcium",
    "Iron",
    "Magnesium",
    "Phosphorus",
    "Zinc",
    "Vitamin C",
    "Vitamin D",
    "Vitamin A",
    "Vitamin E",
    "Vitamin K",
    "Folate",
    "Vitamin B-12",
    "Thiamin",
    "Riboflavin",
    "Niacin",
]


def find_file(root_folder, filename):
    matches = list(root_folder.rglob(filename))

    if not matches:
        return None

    return matches[0]


for dataset_name, dataset_folder in DATASETS.items():

    print("\n" + "=" * 80)
    print(dataset_name)
    print("=" * 80)

    nutrient_file = find_file(dataset_folder, "nutrient.csv")

    if nutrient_file is None:
        print("nutrient.csv not found")
        continue

    df = pd.read_csv(nutrient_file)

    # Search nutrient names
    pattern = "|".join(SEARCH_TERMS)

    matches = df[
        df["name"]
        .astype(str)
        .str.contains(pattern, case=False, na=False)
    ]

    print("\nRelevant nutrients found:")
    print(
        matches[
            ["id", "name", "unit_name", "nutrient_nbr"]
        ].to_string(index=False)
    )