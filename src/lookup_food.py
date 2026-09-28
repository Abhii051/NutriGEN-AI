
import pandas as pd
import os

# Load USDA food database
df = pd.read_csv(
    "data/processed/foods_combined_classified.csv"
)

# Load custom foods, if the file exists
custom_path = "data/processed/custom_foods.csv"

if os.path.exists(custom_path):
    custom_df = pd.read_csv(custom_path)
    df = pd.concat([df, custom_df], ignore_index=True)

print("NutriGEN-AI Food Database")
print("Type 'exit' to quit.")

while True:
    food = input("\nEnter food name: ").strip()

    if food.lower() == "exit":
        break

    results = df[
        df["food_name"].str.contains(
            food,
            case=False,
            na=False,
            regex=False
        )
    ]

    if results.empty:
        print("Food not found in database.")
        continue

    print("\nMatching foods:")

    for _, row in results.head(10).iterrows():
        print(f"\nFood: {row['food_name']}")
        print(f"Category: {row['food_type']}")
        print(f"Source: {row['source']}")
        print(f"Calories: {row['calories']} kcal")
        print(f"Protein: {row['protein_g']} g")
        print(f"Fat: {row['fat_g']} g")
        print(f"Carbs: {row['carbs_g']} g")