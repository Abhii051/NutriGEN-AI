
import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "foods_combined_clean.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "foods_combined_classified.csv"
)


def classify_food(food_name):
    """Classify food using preliminary name-based keywords."""

    name = str(food_name).lower().strip()

    # Non-vegetarian foods
    non_vegetarian_keywords = [
        "chicken", "beef", "pork", "turkey",
        "fish", "salmon", "pollock", "tuna",
        "shrimp", "prawn", "crab", "lobster",
        "lamb", "mutton", "duck", "goat",
        "bacon", "ham", "sausage", "anchovy",
        "sardine", "meat", "oyster", "clam",
        "mussel", "squid", "octopus",
        "venison", "veal", "trout", "cod",
        "haddock", "herring", "swordfish",
        "tilapia", "catfish", "halibut",
        "scallop", "frog legs", "quail",
        "pheasant", "goose", "rabbit",
        "liver", "kidney", "heart",
        "lard", "gelatin","ascidians"
    ]

    # Vegetarian foods containing animal-derived ingredients
    # These are not classified as vegan.
    vegetarian_keywords = [
        "milk", "cheese", "yogurt", "yoghurt",
        "butter", "cream", "egg", "whey",
        "casein", "ghee", "honey",
        "curd", "paneer", "custard",
        "mayonnaise", "mayonna ise",
        "lactose", "lactalbumin"
    ]

    # Plant-based foods
    vegan_keywords = [
        # Fruits
        "fruit", "apricot", "apple", "banana",
        "orange", "fig", "mango", "melon",
        "nectarine", "plantain", "plum",
        "strawberry", "blueberry", "raspberry",
        "grape", "pear", "peach", "cherry",
        "pineapple", "papaya", "guava",
        "watermelon", "kiwi", "lemon", "lime","abiyuch",
        "acerola","agave",

        # Vegetables
        "vegetable", "arugula", "asparagus",
        "beet", "brussels sprouts", "cabbage",
        "cauliflower", "collards", "fennel",
        "kale", "lettuce", "parsnip",
        "radicchio", "radish", "squash",
        "zucchini", "turnip", "spinach",
        "carrot", "broccoli", "potato",
        "tomato", "onion", "garlic",
        "mushroom", "celery", "cucumber",
        "eggplant", "okra", "yam",
        "sweet potato", "artichoke",
        "bamboo shoot", "green bean",

        # Grains and cereals
        "rice", "wheat", "bulgur", "einkorn",
        "fonio", "khorasan", "millet", "sorghum",
        "oat", "barley", "corn", "quinoa",
        "buckwheat", "flour", "bran",
        "rye", "spelt", "amaranth", "teff",
        "couscous", "pasta",

        # Legumes, nuts and seeds
        "lentil", "bean", "pea", "chickpea",
        "almond", "peanut", "cashew", "walnut",
        "brazilnut", "hazelnut", "filbert",
        "macadamia", "pecan", "pine nut",
        "pistachio", "seed", "tofu", "soy",
        "soybean", "edamame", "tempeh",
        # Additional plant-based foods
        "arrowhead",
        "arrowroot",
        "avocado",
        "baobab",
        "basil",
        # Other plant-based foods
        "coconut", "olive", "hummus",
        "plant-based", "vegetable oil",
        "olive oil", "canola oil",
        "sunflower oil", "sesame oil",
        "maple syrup", "molasses",
        "salsa", "guacamole"
    ]

    # Check non-vegetarian first
    for keyword in non_vegetarian_keywords:
        if keyword in name:
            return "non_vegetarian"

    # Check vegetarian animal-derived ingredients
    for keyword in vegetarian_keywords:
        if keyword in name:
            return "vegetarian"

    # Check plant-based foods
    for keyword in vegan_keywords:
        if keyword in name:
            return "vegan"

    # Do not guess when the name is insufficient
    return "unknown"


def main():

    print("Loading combined food dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print("Total foods loaded:", len(df))

    # Classify each food
    df["food_type"] = df["food_name"].apply(
        classify_food
    )

    # Save to a new file
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nClassification completed!")

    print("Total foods:", len(df))

    print("\nFood category counts:")
    print(
        df["food_type"]
        .value_counts()
        .reindex(
            [
                "vegan",
                "vegetarian",
                "non_vegetarian",
                "unknown"
            ],
            fill_value=0
        )
    )

    print("\nFood category percentages:")
    print(
        (
            df["food_type"]
            .value_counts(normalize=True)
            * 100
        ).round(2)
    )

    print("\nRecords by source:")
    print(
        df.groupby(
            ["source", "food_type"]
        ).size()
    )

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()