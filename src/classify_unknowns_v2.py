
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "foods_final_cleaned.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

df = pd.read_csv(INPUT_FILE)

# Only process foods that are currently unknown.
mask = df["food_type"].astype(str).str.lower().str.strip() == "unknown"

# Conservative, name-based rules.
# Do not change existing non-unknown labels.
vegan_terms = [
    "avocado", "arrowroot", "arrowhead",
    "agave", "abiyuch", "acerola",
    "acorn", "apple", "apricot", "banana",
    "barley", "beans", "beet", "berries",
    "broccoli", "cabbage", "carrot",
    "cauliflower", "celery", "cherry",
    "chickpeas", "coconut", "corn",
    "cucumber", "dates", "eggplant",
    "fig", "garlic", "ginger", "grapes",
    "guava", "jackfruit", "kale", "lentils",
    "lettuce", "mango", "millet", "okra",
    "onion", "orange", "papaya", "peach",
    "peanuts", "pear", "peas", "pineapple",
    "plum", "potato", "pumpkin", "radish",
    "rice", "spinach", "sweet potato",
    "tapioca", "tomato", "turnip", "yam",
    "zucchini"
]

non_veg_terms = [
    "beef", "pork", "chicken", "turkey",
    "duck", "goose", "lamb", "mutton",
    "venison", "bison", "buffalo meat",
    "fish", "salmon", "tuna", "cod",
    "pollock", "anchovy", "anchovies",
    "sardine", "shrimp", "prawn", "crab",
    "lobster", "oyster", "clam", "mussel",
    "scallop", "squid", "octopus", "meat",
    "bacon", "ham", "sausage", "steak",
    "veal", "liver", "anchovy"
]

def classify_food(name):
    name = str(name).lower().strip()

    # Clear animal-derived ingredients take precedence.
    if any(term in name for term in non_veg_terms):
        return "non_vegetarian"

    # Clearly named plant-based foods.
    if any(term in name for term in vegan_terms):
        return "vegan"

    return "unknown"

df["food_type_v2"] = df["food_type"]

df.loc[mask, "food_type_v2"] = (
    df.loc[mask, "food_name"].apply(classify_food)
)

df["classification_method"] = "existing_label"

df.loc[mask & (df["food_type_v2"] != "unknown"),
       "classification_method"] = "keyword_suggestion_unverified"

df.loc[mask & (df["food_type_v2"] == "unknown"),
       "classification_method"] = "needs_manual_review"

output_file = OUTPUT_DIR / "foods_classified_v2.csv"
review_file = OUTPUT_DIR / "foods_v2_needing_review.csv"

df.to_csv(output_file, index=False)

df[df["food_type_v2"] == "unknown"].to_csv(
    review_file, index=False
)

print("Original records:", len(df))
print("\nNew label counts:")
print(df["food_type_v2"].value_counts())

print("\nExisting labels preserved:", 
      (df.loc[~mask, "food_type_v2"] ==
       df.loc[~mask, "food_type"]).all())

print("\nClassified dataset saved:", output_file)
print("Remaining review records:", review_file)