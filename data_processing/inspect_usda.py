from pathlib import Path
import pandas as pd


# Project root = folder from which we run the script
PROJECT_ROOT = Path.cwd()

DATASETS = {
    "Foundation": PROJECT_ROOT / "data" / "raw" / "foundation",
    "SR Legacy": PROJECT_ROOT / "data" / "raw" / "sr_legacy",
}

FILES_TO_INSPECT = [
    "food.csv",
    "food_nutrient.csv",
    "nutrient.csv",
    "food_category.csv",
]


def find_file(root_folder, filename):
    """
    Search recursively for a CSV file.
    This handles USDA's nested folder structure.
    """
    matches = list(root_folder.rglob(filename))

    if not matches:
        return None

    if len(matches) > 1:
        print(f"\nWARNING: Multiple {filename} files found:")
        for match in matches:
            print("  ", match)

    return matches[0]


def inspect_file(dataset_name, dataset_folder, filename):
    print("\n" + "=" * 70)
    print(f"{dataset_name} -> {filename}")
    print("=" * 70)

    file_path = find_file(dataset_folder, filename)

    if file_path is None:
        print("FILE NOT FOUND")
        return

    print(f"Path: {file_path}")

    try:
        df = pd.read_csv(file_path, nrows=5)

        print("\nColumns:")
        for column in df.columns:
            print(" -", column)

        print("\nFirst 5 rows:")
        print(df.to_string(index=False))

    except Exception as e:
        print(f"ERROR reading file: {e}")


def main():
    for dataset_name, dataset_folder in DATASETS.items():

        print("\n\n")
        print("#" * 70)
        print(f"# {dataset_name}")
        print("#" * 70)

        if not dataset_folder.exists():
            print(f"Dataset folder not found: {dataset_folder}")
            continue

        for filename in FILES_TO_INSPECT:
            inspect_file(
                dataset_name,
                dataset_folder,
                filename
            )


if __name__ == "__main__":
    main()