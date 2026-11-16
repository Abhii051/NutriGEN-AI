import pandas as pd


def classify_candidate_role(description):
    text = str(description).lower()

    # ---------------------------------------------------------
    # 1. Exclude foods that should not be meal ingredients
    # ---------------------------------------------------------
    excluded_terms = [
        "babyfood",
        "baby food",
        "candy",
        "cookie",
        "cookies",
        "cake",
        "donut",
        "doughnut",
        "pastry",
        "dessert",
        "soft drink",
        "soda",
        "carbonated",
        "alcohol",
        "beer",
        "wine",
        "cereal bar",
        "energy bar",
        "protein bar",
        "supplement",
        "formula",
        "fatty acids",
        "folate,",
        "pantothenic acid,",
        "riboflavin,",
        "thiamin,",
        "niacin,",
        "vitamin ",
    ]

    if any(term in text for term in excluded_terms):
        return "other"

    # ---------------------------------------------------------
    # 2. Healthy fats / oils
    # Check BEFORE staple because "wheat germ oil" contains wheat
    # ---------------------------------------------------------
    healthy_fat_terms = [
        "almond",
        "cashew",
        "walnut",
        "pistachio",
        "pecan",
        "hazelnut",
        "macadamia",
        "chia",
        "flax",
        "sesame",
        "sunflower seed",
        "pumpkin seed",
        "olive oil",
        "canola oil",
        "mustard oil",
        "sesame oil",
        "sunflower oil",
        "coconut oil",
        "avocado",
        "avocado oil",
        "wheat germ oil",
    ]

    if any(term in text for term in healthy_fat_terms):
        return "healthy_fat"

    # ---------------------------------------------------------
    # 3. Protein foods
    # ---------------------------------------------------------
    protein_terms = [
        "lentil",
        "dal",
        "chickpea",
        "chana",
        "bean",
        "rajma",
        "kidney bean",
        "black bean",
        "mung bean",
        "moong",
        "urad",
        "toor",
        "pigeon pea",
        "soy",
        "soya",
        "soybean",
        "tofu",
        "tempeh",
        "egg",
        "egg white",
        "paneer",
        "cottage cheese",
        "chicken",
        "turkey",
        "beef",
        "pork",
        "lamb",
        "mutton",
        "fish",
        "salmon",
        "tuna",
        "sardine",
        "anchovy",
        "trout",
        "shrimp",
        "prawn",
    ]

    if any(term in text for term in protein_terms):
        return "protein"

    # ---------------------------------------------------------
    # 4. Vegetables
    # ---------------------------------------------------------
    vegetable_terms = [
        "spinach",
        "broccoli",
        "cauliflower",
        "carrot",
        "cabbage",
        "okra",
        "bhindi",
        "eggplant",
        "brinjal",
        "tomato",
        "cucumber",
        "pumpkin",
        "gourd",
        "zucchini",
        "pepper",
        "beet",
        "radish",
        "turnip",
        "onion",
        "garlic",
        "green bean",
        "vegetable",
        "drumstick",
    ]

    if any(term in text for term in vegetable_terms):
        return "vegetable"

    # ---------------------------------------------------------
    # 5. Fruits
    # ---------------------------------------------------------
    fruit_terms = [
        "apple",
        "banana",
        "orange",
        "mango",
        "papaya",
        "pineapple",
        "grape",
        "berry",
        "strawberry",
        "blueberry",
        "watermelon",
        "melon",
        "guava",
        "pomegranate",
        "pear",
        "peach",
        "plum",
        "kiwi",
        "cherry",
        "fig",
        "date",
        "raisin",
        "groundcherries",
        "cape-gooseberries",
    ]

    if any(term in text for term in fruit_terms):
        return "fruit"

    # ---------------------------------------------------------
    # 6. Dairy
    # ---------------------------------------------------------
    dairy_terms = [
        "milk",
        "yogurt",
        "yoghurt",
        "curd",
        "paneer",
        "cheese",
        "cream",
        "butter",
        "ghee",
    ]

    if any(term in text for term in dairy_terms):
        return "dairy"

    # ---------------------------------------------------------
    # 7. Staple foods
    # Keep generic terms such as wheat/rice LAST
    # ---------------------------------------------------------
    staple_terms = [
        "rice",
        "wheat",
        "atta",
        "roti",
        "chapati",
        "paratha",
        "naan",
        "oat",
        "oats",
        "barley",
        "millet",
        "ragi",
        "jowar",
        "bajra",
        "quinoa",
        "potato",
        "sweet potato",
        "corn",
        "maize",
        "poha",
        "upma",
    ]

    if any(term in text for term in staple_terms):
        return "staple"

    return "other"

def add_candidate_roles(df):
    df = df.copy()

    df["food_role"] = df["description"].apply(
        classify_candidate_role
    )

    return df


def select_candidate_pool(
    df,
    max_per_role=100
):
    df = add_candidate_roles(df)

    selected_groups = []

    roles = [
        "staple",
        "protein",
        "vegetable",
        "fruit",
        "healthy_fat",
        "dairy",
    ]

    for role in roles:

        role_df = df[df["food_role"] == role].copy()

        # Prefer Indian foods
        if "cuisine_score" in role_df.columns:
            role_df = role_df.sort_values(
                by="cuisine_score",
                ascending=False
            )

        role_df = role_df.head(max_per_role)

        selected_groups.append(role_df)

    candidate_pool = pd.concat(
        selected_groups,
        ignore_index=True
    )

    return candidate_pool.reset_index(drop=True)