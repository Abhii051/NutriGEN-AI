import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "foods_clean.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "foods_classified.csv"


def classify_food(food_name):
    name = food_name.lower()

    # Non-vegetarian foods
    non_vegetarian_keywords = [
        "chicken", "beef", "pork", "turkey", "fish",
        "salmon", "pollock", "tuna", "shrimp", "prawn",
        "crab", "lobster", "lamb", "mutton", "duck",
        "goat", "bacon", "ham", "sausage", "anchovy",
        "sardine", "meat", "oyster", "clam", "mussel"
    ]

    # Animal-derived ingredients that are vegetarian
    vegetarian_keywords = [
        "milk", "cheese", "yogurt", "yoghurt", "butter",
        "cream", "egg", "whey", "casein", "ghee",
        "honey"
    ]

    # Foods commonly containing animal products
    for keyword in non_vegetarian_keywords:
        if keyword in name:
            return "non_vegetarian"

    for keyword in vegetarian_keywords:
        if keyword in name:
            return "vegetarian"

    # Plant-based ingredients
        vegan_keywords = [
        # Fruits
        "fruit", "apricot", "apple", "banana", "orange",
        "fig", "mango", "melon", "nectarine", "plantain",
        "plum", "strawberr",

        # Vegetables
        "vegetable", "arugula", "asparagus", "beet",
        "brussels sprouts", "cabbage", "cauliflower",
        "collards", "fennel", "kale", "lettuce",
        "parsnip", "pepper", "radicchio", "radish",
        "squash", "zucchini", "turnip", "spinach",
        "carrot", "broccoli", "potato", "tomato",
        "onion", "garlic", "mushroom",

        # Grains and cereals
        "rice", "wheat", "bulgur", "einkorn",
        "fonio", "khorasan", "millet", "sorghum",
        "oat", "barley", "corn", "quinoa",
        "buckwheat", "flour", "bran",

        # Legumes, nuts and seeds
        "lentil", "bean", "pea", "chickpea",
        "almond", "peanut", "cashew", "walnut",
        "brazilnut", "hazelnut", "filbert",
        "macadamia", "pecan", "pine nut",
        "pistachio", "seed", "tofu", "soy",

        # Other plant-based foods
        "coconut", "olive", "hummus",
        ]

    for keyword in vegan_keywords:
        if keyword in name:
            return "vegan"

    return "unknown"


def main():
    print("Loading food dataset...")

    df = pd.read_csv(INPUT_FILE)

    df["food_type"] = df["food_name"].apply(classify_food)

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nClassification completed!")
    print("Total foods:", len(df))

    print("\nFood category counts:")
    print(df["food_type"].value_counts())

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()