
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "foods_final_cleaned.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

REVIEW_FILE = (
    OUTPUT_DIR / "unknown_foods_suggestions.csv"
)

# ==========================================
# 2. LOAD DATA
# ==========================================

df = pd.read_csv(INPUT_FILE)

unknown = df[
    df["food_type"].astype(str).str.lower().eq("unknown")
].copy()

print("Unknown foods:", len(unknown))

# ==========================================
# 3. CONSERVATIVE KEYWORD SUGGESTIONS
# ==========================================

# These rules suggest a label only when a food name
# contains a relatively clear ingredient indicator.
# Suggestions require review before acceptance.

nonveg_terms = [
    "chicken", "turkey", "beef", "pork",
    "lamb", "mutton", "goat meat", "duck",
    "quail", "venison", "bison", "rabbit",
    "anchovy", "anchovies", "sardine",
    "salmon", "tuna", "cod", "shrimp",
    "prawn", "crab", "lobster", "clam",
    "oyster", "mussel", "squid", "octopus",
    "fish", "meat", "bacon", "ham",
    "sausage", "pepperoni", "prosciutto",
    "egg", "eggs", "gelatin", "lard"
]

vegan_terms = [
    "lentil", "lentils", "chickpea",
    "chickpeas", "black bean", "kidney bean",
    "pinto bean", "navy bean", "tofu",
    "tempeh", "seitan", "quinoa",
    "brown rice", "white rice", "oats",
    "oatmeal", "almond", "cashew",
    "walnut", "peanut", "pecan",
    "sunflower seed", "pumpkin seed",
    "flaxseed", "chia seed", "broccoli",
    "spinach", "carrot", "potato",
    "sweet potato", "tomato", "apple",
    "banana", "orange", "mango",
    "blueberry", "strawberry", "mushroom"
]

vegetarian_terms = [
    "milk", "cheese", "paneer",
    "yogurt", "yoghurt", "curd",
    "butter", "cream", "ghee",
    "mozzarella", "cheddar",
    "parmesan", "ricotta", "whey",
    "casein", "cottage cheese"
]

def suggest_category(name):
    name = str(name).lower()

    # Non-vegetarian indicators take priority.
    if any(term in name for term in nonveg_terms):
        return "non_vegetarian"

    if any(term in name for term in vegetarian_terms):
        return "vegetarian"

    if any(term in name for term in vegan_terms):
        return "vegan"

    return "needs_manual_review"


# ==========================================
# 4. GENERATE SUGGESTIONS
# ==========================================

unknown["suggested_food_type"] = (
    unknown["food_name"].apply(suggest_category)
)

unknown["review_status"] = "NOT_VERIFIED"

unknown.to_csv(REVIEW_FILE, index=False)

# ==========================================
# 5. SUMMARY
# ==========================================

print("\n========== SUGGESTION SUMMARY ==========")

print(
    unknown["suggested_food_type"]
    .value_counts()
    .to_string()
)

print("\nTotal unknown records:", len(unknown))

print("\nReview file saved to:")
print(REVIEW_FILE)

print("\nNo original labels have been changed.")