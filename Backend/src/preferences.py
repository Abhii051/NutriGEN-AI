import re
import pandas as pd


# =========================================================
# USER PREFERENCES
# =========================================================

def create_preferences(
    diet_type="vegetarian",
    eats_eggs=False,
    cuisine="indian",
    allergies=None,
    disliked_foods=None,
    number_of_meals=3,
    number_of_snacks=1,
):
    """
    Create and validate the user's food preferences.
    """

    if allergies is None:
        allergies = []

    if disliked_foods is None:
        disliked_foods = []

    diet_type = diet_type.lower().strip()
    cuisine = cuisine.lower().strip()

    valid_diets = [
        "vegetarian",
        "vegan",
        "non-vegetarian",
    ]

    if diet_type not in valid_diets:
        raise ValueError(
            "diet_type must be vegetarian, vegan, or non-vegetarian."
        )

    if number_of_meals not in [3, 4, 5]:
        raise ValueError(
            "number_of_meals must be 3, 4, or 5."
        )

    if number_of_snacks not in [0, 1, 2]:
        raise ValueError(
            "number_of_snacks must be 0, 1, or 2."
        )

    # Eggs are relevant only for vegetarians.
    if diet_type != "vegetarian":
        eats_eggs = False

    return {
        "diet_type": diet_type,
        "eats_eggs": bool(eats_eggs),
        "cuisine": cuisine,
        "allergies": [
            str(item).lower().strip()
            for item in allergies
        ],
        "disliked_foods": [
            str(item).lower().strip()
            for item in disliked_foods
        ],
        "number_of_meals": number_of_meals,
        "number_of_snacks": number_of_snacks,
    }


# =========================================================
# TEXT MATCHING
# =========================================================

def contains_food_term(text, terms):
    text = str(text).lower()

    for term in terms:
        term = str(term).lower().strip()

        if not term:
            continue

        # Match the exact term
        pattern = r"\b" + re.escape(term) + r"\b"

        if re.search(pattern, text):
            return True

        # Also handle common plural forms
        if not term.endswith("s"):
            plural_pattern = r"\b" + re.escape(term + "s") + r"\b"

            if re.search(plural_pattern, text):
                return True

    return False

# =========================================================
# DIET FILTER
# =========================================================

def apply_diet_filter(df, preferences):
    """
    Remove foods that do not match the selected diet.
    """

    df = df.copy()

    descriptions = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    diet_type = preferences["diet_type"]
    eats_eggs = preferences["eats_eggs"]

    # -----------------------------------------------------
    # Animal foods
    # -----------------------------------------------------

    meat_terms = [
        "beef",
        "pork",
        "lamb",
        "mutton",
        "goat",
        "veal",
        "venison",
        "bison",
        "meat",
        "steak",
        "ham",
        "bacon",
        "sausage",
        "salami",
        "pepperoni",
        "prosciutto",
        "chicken",
        "turkey",
        "duck",
        "poultry",
        "fish",
        "salmon",
        "tuna",
        "sardine",
        "anchovy",
        "trout",
        "seafood",
        "shrimp",
        "prawn",
        "crab",
        "lobster",
        "shellfish",
        "clam",
        "oyster",
        "mussel",
    ]

    # -----------------------------------------------------
    # Egg foods
    # -----------------------------------------------------

    egg_terms = [
        "egg",
        "eggs",
        "egg white",
        "egg yolk",
        "omelet",
        "omelette",
    ]

    # -----------------------------------------------------
    # Dairy foods
    # -----------------------------------------------------

    dairy_terms = [
        "milk",
        "cheese",
        "yogurt",
        "yoghurt",
        "curd",
        "paneer",
        "cream",
        "butter",
        "ghee",
        "whey",
        "casein",
    ]

    # -----------------------------------------------------
    # Vegan filtering
    # -----------------------------------------------------

    if diet_type == "vegan":

        animal_pattern = (
            meat_terms
            + egg_terms
            + dairy_terms
        )

        mask = ~descriptions.apply(
            lambda text: contains_food_term(
                text,
                animal_pattern
            )
        )

        df = df[mask]

    # -----------------------------------------------------
    # Vegetarian filtering
    # -----------------------------------------------------

    elif diet_type == "vegetarian":

        mask = ~descriptions.apply(
            lambda text: contains_food_term(
                text,
                meat_terms
            )
        )

        df = df[mask]

        # Remove eggs if user does not eat eggs.
        if not eats_eggs:

            mask = ~df["description"].fillna("").astype(str).str.lower().apply(
                lambda text: contains_food_term(
                    text,
                    egg_terms
                )
            )

            df = df[mask]

    # -----------------------------------------------------
    # Non-vegetarian
    # -----------------------------------------------------

    elif diet_type == "non-vegetarian":

        # No meat/egg/dairy restriction.
        pass

    return df.reset_index(drop=True)


# =========================================================
# ALLERGY FILTER
# =========================================================

def apply_allergy_filter(df, preferences):
    df = df.copy()
    allergies = preferences["allergies"]

    if not allergies:
        return df.reset_index(drop=True)

    allergy_aliases = {
        "peanut": [
            "peanut",
            "groundnut",
            "arachis"
        ],

        "tree_nuts": [
            "almond",
            "cashew",
            "walnut",
            "pistachio",
            "pecan",
            "hazelnut",
            "macadamia",
            "brazil nut"
        ],

        "milk": [
            "milk",
            "whey",
            "casein",
            "cheese",
            "yogurt",
            "yoghurt",
            "curd",
            "paneer",
            "cream",
            "butter",
            "ghee"
        ],

        "egg": [
            "egg",
            "albumen",
            "egg white",
            "egg yolk"
        ],

        "soy": [
            "soy",
            "soya",
            "soybean",
            "tofu",
            "tempeh",
            "miso",
            "edamame"
        ],

        "wheat": [
            "wheat",
            "flour",
            "atta",
            "semolina",
            "durum",
            "bulgur",
            "couscous",
            "gluten"
        ],

        "fish": [
            "fish",
            "salmon",
            "tuna",
            "sardine",
            "anchovy",
            "trout",
            "cod"
        ],

        "shellfish": [
            "shrimp",
            "prawn",
            "crab",
            "lobster",
            "clam",
            "oyster",
            "mussel",
            "shellfish"
        ]
    }

    expanded_terms = []

    for allergy in allergies:
        allergy = allergy.lower().strip()

        if allergy in allergy_aliases:
            expanded_terms.extend(allergy_aliases[allergy])
        else:
            expanded_terms.append(allergy)

    mask = ~df["description"].fillna("").astype(str).str.lower().apply(
        lambda text: contains_food_term(text, expanded_terms)
    )

    return df[mask].reset_index(drop=True)


# =========================================================
# DISLIKED FOOD FILTER
# =========================================================

def apply_disliked_food_filter(df, preferences):
    """
    Remove foods the user does not like.
    """

    df = df.copy()

    disliked_foods = preferences["disliked_foods"]

    if not disliked_foods:
        return df.reset_index(drop=True)

    mask = ~df["description"].fillna("").astype(str).str.lower().apply(
        lambda text: contains_food_term(
            text,
            disliked_foods
        )
    )

    return df[mask].reset_index(drop=True)


# =========================================================
# INDIAN FOOD PRIORITY
# =========================================================

def calculate_cuisine_score(df, preferences):
    """
    Give Indian foods a higher preference score.

    This does NOT remove non-Indian foods.
    """

    df = df.copy()

    cuisine = preferences["cuisine"]

    df["cuisine_score"] = 0

    if cuisine != "indian":
        return df

    indian_food_terms = [
        # Staples
        "basmati",
        "rice",
        "atta",
        "wheat",
        "roti",
        "chapati",
        "millet",
        "ragi",
        "jowar",
        "bajra",

        # Pulses / legumes
        "dal",
        "lentil",
        "chickpea",
        "chana",
        "rajma",
        "kidney bean",
        "mung",
        "moong",
        "urad",
        "toor",
        "pigeon pea",

        # Indian vegetables / foods
        "okra",
        "bhindi",
        "brinjal",
        "eggplant",
        "baingan",
        "gourd",
        "bottle gourd",
        "bitter gourd",
        "ridge gourd",
        "drumstick",

        # Dairy / protein
        "paneer",
        "curd",
        "dahi",

        # Spices
        "turmeric",
        "cumin",
        "jeera",
        "coriander",
        "cardamom",
        "clove",
        "ginger",
        "garlic",

        # Common Indian foods
        "poha",
        "upma",
        "idli",
        "dosa",
        "sambar",
    ]

    df["cuisine_score"] = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.lower()
        .apply(
            lambda text: 1
            if contains_food_term(
                text,
                indian_food_terms
            )
            else 0
        )
    )

    return df

def deduplicate_candidates(df):
    df = df.copy()

    # Create a normalized description
    df["description_key"] = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Prefer Indian foods when cuisine preference is Indian
    if "cuisine_score" in df.columns:
        df = df.sort_values(
            by=["cuisine_score"],
            ascending=False
        )


    # Keep only one representative of each food description
    df = df.drop_duplicates(
        subset=["description_key"],
        keep="first"
    )

    return df.drop(
        columns=["description_key"]
    ).reset_index(drop=True)
# =========================================================
# COMPLETE PREFERENCE PIPELINE
# =========================================================

def apply_preferences(df, preferences):
    df = apply_diet_filter(df, preferences)
    df = apply_allergy_filter(df, preferences)
    df = apply_disliked_food_filter(df, preferences)
    df = calculate_cuisine_score(df, preferences)

    print("Before deduplication:", len(df))

    df = deduplicate_candidates(df)

    print("After deduplication:", len(df))

    return df.reset_index(drop=True)


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    preferences = create_preferences(
        diet_type="vegetarian",
        eats_eggs=True,
        cuisine="indian",
        allergies=["peanuts"],
        disliked_foods=["mushroom"],
        number_of_meals=3,
        number_of_snacks=1,
    )

    print("\n===== USER PREFERENCES =====")

    for key, value in preferences.items():
        print(f"{key}: {value}")