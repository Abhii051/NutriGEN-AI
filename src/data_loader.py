import pandas as pd


DATA_PATH = "data/raw/foods.csv"


def load_food_data():
    return pd.read_csv(DATA_PATH)


def validate_food_data(df):

    required_columns = [
        "food_id",
        "food_name",
        "calories",
        "protein_g",
        "carbs_g",
        "fat_g",
        "fiber_g",
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing column: {column}")

    if df.empty:
        raise ValueError("Food dataset is empty.")

    if df["food_name"].isnull().any():
        raise ValueError("Food name cannot be empty.")

    return True


if __name__ == "__main__":

    foods = load_food_data()

    validate_food_data(foods)

    print("Food dataset loaded successfully.")
    print(f"Number of foods: {len(foods)}")

    print("\nAvailable foods:")
    print(foods[["food_id", "food_name"]])