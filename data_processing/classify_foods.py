import re
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "master_food_dataset.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "master_food_dataset_classified.csv"


# ---------------------------------------------------------
# 1. DEFINITE NON-VEGETARIAN FOODS
# ---------------------------------------------------------

NON_VEGETARIAN_TERMS = [
    "beef",
    "pork",
    "chicken",
    "turkey",
    "duck",
    "goose",
    "lamb",
    "veal",
    "mutton",
    "goat meat",
    "venison",
    "bison",
    "buffalo meat",
    "rabbit",
    "bacon",
    "ham",
    "sausage",
    "salami",
    "pepperoni",
    "prosciutto",
    "luncheon meat",

    "fish",
    "tuna",
    "salmon",
    "cod",
    "sardine",
    "anchovy",
    "trout",
    "herring",
    "mackerel",
    "haddock",
    "pollock",
    "tilapia",
    "catfish",
    "swordfish",

    "shrimp",
    "prawn",
    "lobster",
    "crab",
    "clam",
    "oyster",
    "mussel",
    "scallop",
    "squid",
    "octopus",
    "shellfish",
    "seafood",
    "caviar",
    "roe",

    "gelatin",
    "lard",
    "tallow",
    "bone broth",
    "chicken broth",
    "chicken stock",
    "beef broth",
    "beef stock",
    "fish sauce",
    "anchovy paste",
]


# ---------------------------------------------------------
# 2. DAIRY / EGG FOODS
# These are vegetarian but NOT vegan.
# ---------------------------------------------------------

DAIRY_EGG_TERMS = [
    "cow milk",
    "whole milk",
    "skim milk",
    "lowfat milk",
    "milk",
    "buttermilk",
    "cheese",
    "yogurt",
    "yoghurt",
    "cream",
    "butter",
    "ghee",
    "whey",
    "casein",
    "lactose",
    "cottage cheese",
    "cream cheese",
    "parmesan",
    "mozzarella",
    "cheddar",
    "ricotta",
    "feta",
    "egg",
    "eggs",
    "egg yolk",
    "egg white",
    "mayonnaise",
]


# ---------------------------------------------------------
# 3. ANIMAL-DERIVED INGREDIENTS
# ---------------------------------------------------------

ANIMAL_DERIVED_TERMS = [
    "honey",
    "beeswax",
    "royal jelly",
]


# ---------------------------------------------------------
# 4. DEFINITE PLANT-BASED FOODS
# ---------------------------------------------------------

PLANT_TERMS = [
    "vegetable",
    "fruit",
    "legume",
    "bean",
    "beans",
    "lentil",
    "lentils",
    "pea",
    "peas",
    "chickpea",
    "chickpeas",

    "tofu",
    "tempeh",
    "soy",
    "soya",

    "rice",
    "oat",
    "oats",
    "wheat",
    "barley",
    "rye",
    "quinoa",
    "corn",
    "maize",
    "millet",
    "sorghum",
    "buckwheat",
    "amaranth",
    "bulgur",
    "fonio",

    "flax",
    "chia",
    "sesame",

    "almond",
    "almonds",
    "cashew",
    "cashews",
    "walnut",
    "walnuts",
    "pecan",
    "pecans",
    "pistachio",
    "pistachios",
    "peanut",
    "peanuts",
    "chestnut",
    "pine nut",
    "pine nuts",
    "brazil nut",
    "brazil nuts",

    "sunflower seed",
    "pumpkin seed",

    "olive oil",
    "safflower oil",
    "sunflower oil",
    "canola oil",
    "vegetable oil",
    "coconut",
    "avocado",

    "mushroom",
    "mushrooms",

    "lettuce",
    "spinach",
    "cabbage",
    "carrot",
    "carrots",
    "tomato",
    "tomatoes",
    "onion",
    "onions",
    "leek",
    "leeks",
    "radish",
    "radishes",

    "salsa",
    "pasta",
]


# ---------------------------------------------------------
# 5. PLANT-BASED MILKS
# Must be checked BEFORE the generic "milk" rule.
# ---------------------------------------------------------

PLANT_MILKS = [
    "almond milk",
    "soy milk",
    "soya milk",
    "oat milk",
    "rice milk",
    "coconut milk",
    "cashew milk",
    "pea milk",
    "plant milk",
]


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def contains_term(text, terms):
    """
    Match complete words/phrases instead of arbitrary substrings.
    """

    for term in terms:
        pattern = r"\b" + re.escape(term) + r"\b"

        if re.search(pattern, text):
            return True

    return False


# ---------------------------------------------------------
# Classification
# ---------------------------------------------------------

def classify_food(description, category=""):
    text = f"{description} {category}".lower()

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # -----------------------------------------------------
    # Priority 1: Non-vegetarian
    # -----------------------------------------------------

    if contains_term(text, NON_VEGETARIAN_TERMS):
        return "non_vegetarian"

    # -----------------------------------------------------
    # Priority 2: Explicit plant-based milk
    # Must happen BEFORE generic milk.
    # -----------------------------------------------------

    if contains_term(text, PLANT_MILKS):
        return "vegan"

    # -----------------------------------------------------
    # Priority 3: Dairy / eggs / animal-derived
    # -----------------------------------------------------

    if contains_term(text, DAIRY_EGG_TERMS):
        return "vegetarian"

    if contains_term(text, ANIMAL_DERIVED_TERMS):
        return "vegetarian"

    # -----------------------------------------------------
    # Priority 4: Plant-based foods
    # -----------------------------------------------------

    if contains_term(text, PLANT_TERMS):
        return "vegan"

    # -----------------------------------------------------
    # Otherwise we don't know.
    # -----------------------------------------------------

    return "unknown"


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("Loading master dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded {len(df):,} records")

    df["diet_type"] = df.apply(
        lambda row: classify_food(
            row["description"],
            row.get("food_category", "")
        ),
        axis=1
    )

    # Boolean convenience columns
    df["vegan"] = df["diet_type"].eq("vegan")

    df["vegetarian"] = df["diet_type"].isin(
        ["vegan", "vegetarian"]
    )

    df["non_vegetarian"] = df["diet_type"].eq(
        "non_vegetarian"
    )

    # Save
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nClassification complete.")
    print("\nDiet type counts:")
    print(df["diet_type"].value_counts())

    print(f"\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()