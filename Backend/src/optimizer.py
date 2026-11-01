from pathlib import Path
import re

import numpy as np
import pandas as pd
from scipy.optimize import minimize


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_food_dataset_final.csv"
)


# =========================================================
# SETTINGS
# =========================================================

MAX_FOODS = 14


# Foods we do not want in normal meal plans
EXCLUDE_TERMS = [
    "protein powder",
    "protein isolate",
    "protein concentrate",
    "whey protein",
    "soy protein isolate",
    "soy protein concentrate",
    "egg white powder",
    "egg white dried",
    "egg albumen powder",
    "spirulina",
    "collagen",
    "gelatin",
    "supplement",
    "meal replacement",
    "nutrition powder",
    "babyfood",
    "baby food",
    "infant formula",
    "formula",
]


# USDA categories that we want to avoid
EXCLUDE_CATEGORIES = [
    "Fast Foods",
    "Restaurant Foods",
    "Meals, Entrees, and Side Dishes",
    "Sweets",
    "Snacks",
    "Baby Foods",
]


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "fdc_id",
        "description",
        "diet_type",
        "food_category",
        "calories_kcal",
        "protein_g",
        "fat_g",
        "carbohydrate_g",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    numeric_columns = [
        "calories_kcal",
        "protein_g",
        "fat_g",
        "carbohydrate_g",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "description",
            "calories_kcal",
            "protein_g",
            "fat_g",
            "carbohydrate_g",
        ]
    )

    df = df[
        df["calories_kcal"] > 0
    ]

    return df.reset_index(drop=True)


# =========================================================
# DIET FILTER
# =========================================================

def filter_diet(df, diet_type):

    diet_type = diet_type.lower().strip()

    if diet_type == "vegan":

        allowed = ["vegan"]

    elif diet_type == "vegetarian":

        allowed = [
            "vegan",
            "vegetarian",
        ]

    elif diet_type in [
        "non_vegetarian",
        "non-vegetarian",
        "non vegetarian",
    ]:

        allowed = [
            "non_vegetarian"
        ]

    else:

        raise ValueError(
            "diet_type must be vegan, vegetarian, "
            "or non_vegetarian"
        )

    result = df[
        df["diet_type"].isin(allowed)
    ].copy()

    if result.empty:
        raise ValueError(
            f"No foods found for diet type: {diet_type}"
        )

    return result.reset_index(drop=True)


# =========================================================
# REMOVE UNSUITABLE FOODS
# =========================================================

def remove_unsuitable_foods(df):

    df = df.copy()

    descriptions = (
        df["description"]
        .astype(str)
        .str.lower()
    )

    mask = np.ones(
        len(df),
        dtype=bool
    )

    # Remove supplements / baby foods / powders
    for term in EXCLUDE_TERMS:

        mask &= ~descriptions.str.contains(
            re.escape(term),
            regex=True,
            na=False
        )

    df = df[mask].copy()

    # Remove undesirable USDA categories
    category_mask = ~df[
        "food_category"
    ].fillna("").isin(
        EXCLUDE_CATEGORIES
    )

    df = df[category_mask].copy()

    # Remove extremely concentrated protein records
    protein_density = (
        df["protein_g"] / 100
    )

    df = df[
        protein_density <= 0.35
    ]

    # Remove extremely calorie-dense records
    df = df[
        df["calories_kcal"] <= 650
    ]

    return df.reset_index(drop=True)


# =========================================================
# FOOD ROLE
# =========================================================

def classify_food(description):

    text = str(description).lower()

    # =====================================================
    # DESSERT / SWEET / PROCESSED FOODS
    # =====================================================

    excluded_terms = [
        "yokan",
        "cake",
        "cookie",
        "biscuit",
        "donut",
        "doughnut",
        "pastry",
        "pie",
        "candy",
        "chocolate",
        "ice cream",
        "pudding",
        "dessert",
        "sweetened",
        "syrup",
        "candy bar",
        "confection",
    ]

    if any(term in text for term in excluded_terms):
        return "other"

    # =====================================================
    # HEALTHY FATS
    # =====================================================

    fat_terms = [
        "almond",
        "walnut",
        "cashew",
        "peanut",
        "pistachio",
        "pecan",
        "hazelnut",
        "macadamia",
        "sesame seed",
        "sunflower seed",
        "pumpkin seed",
        "chia seed",
        "flax seed",
        "flaxseed",
        "olive oil",
        "avocado",
    ]

    if any(term in text for term in fat_terms):
        return "healthy_fat"

    # =====================================================
    # PROTEIN
    # =====================================================

    protein_terms = [
        "chicken",
        "turkey",
        "beef",
        "pork",
        "lamb",
        "veal",
        "fish",
        "salmon",
        "tuna",
        "shrimp",
        "prawn",
        "egg",
        "tofu",
        "tempeh",
        "lentil",
        "chickpea",
        "bean",
        "paneer",
        "cottage cheese",
        "cheese",
        "yogurt",
        "yoghurt",
        "curd",
        "milk",
    ]

    if any(term in text for term in protein_terms):
        return "protein"

    # =====================================================
    # VEGETABLES
    # =====================================================

    vegetable_terms = [
        "spinach",
        "broccoli",
        "carrot",
        "tomato",
        "cabbage",
        "cauliflower",
        "pepper",
        "onion",
        "lettuce",
        "cucumber",
        "squash",
        "zucchini",
        "okra",
        "eggplant",
        "aubergine",
        "vegetable",
        "green bean",
        "green beans",
        "bok choy",
        "pak-choi",
    ]

    if any(term in text for term in vegetable_terms):
        return "vegetable"

    # =====================================================
    # FRUITS
    # =====================================================

    fruit_terms = [
        "apple",
        "banana",
        "orange",
        "mango",
        "grape",
        "berry",
        "strawberry",
        "blueberry",
        "raspberry",
        "blackberry",
        "pineapple",
        "papaya",
        "watermelon",
        "melon",
        "peach",
        "pear",
        "kiwi",
        "guava",
    ]

    if any(term in text for term in fruit_terms):
        return "fruit"

    # =====================================================
    # STAPLES
    # =====================================================

    staple_terms = [
        "rice",
        "oat",
        "oats",
        "bread",
        "wheat",
        "pasta",
        "noodle",
        "corn",
        "maize",
        "potato",
        "sweet potato",
        "quinoa",
        "barley",
        "millet",
        "roti",
        "chapati",
        "tortilla",
    ]

    if any(term in text for term in staple_terms):
        return "staple"

    return "other"
   

# =========================================================
# ADD FOOD ROLES
# =========================================================

def add_food_roles(df):

    df = df.copy()

    df["food_role"] = (
        df["description"]
        .apply(classify_food)
    )

    return df


# =========================================================
# FOOD QUALITY SCORE
# =========================================================

def calculate_food_score(row):

    description = str(
        row["description"]
    ).lower()

    category = str(
        row["food_category"]
    ).lower()

    score = 0.0

    # Prefer basic food categories
    preferred_categories = [
        "vegetables and vegetable products",
        "fruits and fruit juices",
        "legumes and legume products",
        "cereal grains and pasta",
        "dairy and egg products",
        "nut and seed products",
        "finfish and shellfish products",
        "poultry products",
        "beef products",
        "pork products",
        "lamb, veal, and game products",
    ]

    if category in preferred_categories:
        score += 10

    # Penalize processed indicators
    processed_terms = [
        "frozen",
        "canned",
        "fried",
        "fried",
        "breaded",
        "battered",
        "processed",
        "flavored",
        "sweetened",
        "syrup",
        "margarine",
        "hydrogenated",
        "cream substitute",
        "restaurant",
        "denny",
        "mcdonald",
        "burger king",
    ]

    for term in processed_terms:

        if term in description:
            score -= 4

    # Strong penalty for restaurant foods
    if "restaurant" in description:
        score -= 15

    # Prefer foods with identifiable roles
    if row["food_role"] != "other":
        score += 5

    return score


# =========================================================
# SELECT CANDIDATES
# =========================================================

def select_candidates(df):

    df = df.copy()

    df["food_score"] = df.apply(
        calculate_food_score,
        axis=1
    )

    candidate_parts = []

    role_limits = {
        "staple": 6,
        "protein": 8,
        "vegetable": 8,
        "fruit": 6,
        "healthy_fat": 8,
    }

    for role, limit in role_limits.items():

        role_df = df[
            df["food_role"] == role
        ].copy()

        if role_df.empty:
            continue

        role_df = role_df.sort_values(
            "food_score",
            ascending=False
        )

        candidate_parts.append(
            role_df.head(limit)
        )

    if not candidate_parts:
        raise ValueError(
            "No suitable candidates found."
        )

    result = pd.concat(
        candidate_parts,
        ignore_index=True
    )

    result = result.drop_duplicates(
        subset=["fdc_id"]
    )

    return result.reset_index(drop=True)

# =========================================================
# PORTION LIMITS
# =========================================================

def get_portion_bounds(role):

    if role == "staple":
        return 0, 250

    if role == "protein":
        return 0, 200

    if role == "vegetable":
        return 0, 250

    if role == "fruit":
        return 0, 200

    if role == "healthy_fat":
        return 0, 40

    return 0, 150


# =========================================================
# OPTIMIZATION
# =========================================================

def objective(x):

    total_calories = np.dot(
        calories,
        x
    )

    total_protein = np.dot(
        protein,
        x
    )

    total_fat = np.dot(
        fat,
        x
    )

    total_carbs = np.dot(
        carbs,
        x
    )

    calorie_error = (
        (total_calories - target_calories)
        / target_calories
    )

    protein_error = (
        (total_protein - target_protein)
        / target_protein
    )

    fat_error = (
        (total_fat - target_fat)
        / target_fat
    )

    carb_error = (
        (total_carbs - target_carbs)
        / target_carbs
    )

    # Penalize unnecessarily large portions
    portion_penalty = np.sum(
        (x / 200) ** 2
    )

    # Stronger penalty for missing fat
    fat_shortfall = max(
        0,
        target_fat - total_fat
    ) / target_fat

    # Stronger penalty for excessive carbohydrates
    carb_excess = max(
        0,
        total_carbs - target_carbs
    ) / target_carbs

    return (
        15 * calorie_error ** 2
        + 8 * protein_error ** 2
        + 15 * fat_error ** 2
        + 12 * carb_error ** 2
        + 20 * fat_shortfall ** 2
        + 10 * carb_excess ** 2
        + 0.1 * portion_penalty
    )
# =========================================================
# CALCULATE TOTALS
# =========================================================

def calculate_totals(
    foods,
    quantities
):

    calories = np.sum(
        foods["calories_kcal"].to_numpy()
        * quantities
        / 100
    )

    protein = np.sum(
        foods["protein_g"].to_numpy()
        * quantities
        / 100
    )

    fat = np.sum(
        foods["fat_g"].to_numpy()
        * quantities
        / 100
    )

    carbs = np.sum(
        foods["carbohydrate_g"].to_numpy()
        * quantities
        / 100
    )

    return {
        "calories": calories,
        "protein_g": protein,
        "fat_g": fat,
        "carbs_g": carbs,
    }


# =========================================================
# FOOD OUTPUT
# =========================================================

def make_food_entry(row):

    grams = float(
        row["grams"]
    )

    return {
        "fdc_id": int(
            row["fdc_id"]
        ),

        "food": str(
            row["description"]
        ),

        "grams": round(
            grams,
            1
        ),

        "calories": round(
            float(
                row["calories_kcal"]
                * grams
                / 100
            ),
            1
        ),

        "protein_g": round(
            float(
                row["protein_g"]
                * grams
                / 100
            ),
            1
        ),

        "fat_g": round(
            float(
                row["fat_g"]
                * grams
                / 100
            ),
            1
        ),

        "carbs_g": round(
            float(
                row["carbohydrate_g"]
                * grams
                / 100
            ),
            1
        ),
    }


# =========================================================
# MEAL PLAN CREATION
# =========================================================

def create_meal_plan(
    foods,
    quantities
):

    selected = foods.copy()

    selected["grams"] = quantities

    # Only keep foods actually selected
    selected = selected[
        selected["grams"] >= 20
    ].copy()

    if selected.empty:
        raise ValueError(
            "Optimizer selected no foods."
        )

    # Sort by quantity used
    selected = selected.sort_values(
        "grams",
        ascending=False
    )

    meal_plan = {
        "Breakfast": [],
        "Lunch": [],
        "Dinner": [],
        "Snack": [],
    }

    # -----------------------------------------------------
    # Separate foods by role
    # -----------------------------------------------------

    role_foods = {}

    for role in [
        "staple",
        "protein",
        "vegetable",
        "fruit",
        "healthy_fat",
    ]:

        role_foods[role] = selected[
            selected["food_role"] == role
        ].copy()

    used = set()

    def add_food(meal, role):

        matches = role_foods.get(
            role,
            pd.DataFrame()
        )

        matches = matches[
            ~matches["fdc_id"].isin(used)
        ]

        if matches.empty:
            return

        row = matches.iloc[0]

        meal_plan[meal].append(
            make_food_entry(row)
        )

        used.add(
            row["fdc_id"]
        )

    # -----------------------------------------------------
    # Breakfast
    # -----------------------------------------------------

    add_food(
        "Breakfast",
        "staple"
    )

    add_food(
        "Breakfast",
        "protein"
    )

    add_food(
        "Breakfast",
        "fruit"
    )

    # -----------------------------------------------------
    # Lunch
    # -----------------------------------------------------

    add_food(
        "Lunch",
        "staple"
    )

    add_food(
        "Lunch",
        "protein"
    )

    add_food(
        "Lunch",
        "vegetable"
    )

    add_food(
        "Lunch",
        "healthy_fat"
    )

    # -----------------------------------------------------
    # Dinner
    # -----------------------------------------------------

    add_food(
        "Dinner",
        "staple"
    )

    add_food(
        "Dinner",
        "protein"
    )

    add_food(
        "Dinner",
        "vegetable"
    )

    # -----------------------------------------------------
    # Snack
    # -----------------------------------------------------

    add_food(
        "Snack",
        "fruit"
    )

    add_food(
        "Snack",
        "healthy_fat"
    )

    # -----------------------------------------------------
    # Add remaining meaningful foods
    # -----------------------------------------------------

    remaining = selected[
        ~selected["fdc_id"].isin(used)
    ]

    for _, row in remaining.iterrows():

        if row["grams"] < 30:
            continue

        # Put remaining foods into the meal
        # with the fewest items.
        meal = min(
            meal_plan,
            key=lambda m: len(
                meal_plan[m]
            )
        )

        meal_plan[meal].append(
            make_food_entry(row)
        )

        used.add(
            row["fdc_id"]
        )

    return meal_plan

def calculate_meal_plan_totals(meal_plan):

    totals = {
        "calories": 0.0,
        "protein_g": 0.0,
        "fat_g": 0.0,
        "carbs_g": 0.0,
    }

    for foods in meal_plan.values():

        for food in foods:

            totals["calories"] += food["calories"]
            totals["protein_g"] += food["protein_g"]
            totals["fat_g"] += food["fat_g"]
            totals["carbs_g"] += food["carbs_g"]

    return totals

def filter_nutritionally_useful_foods(df):

    df = df.copy()

    # Remove unknown roles
    df = df[
        df["food_role"] != "other"
    ]

    # Remove nutritionally empty records
    df = df[
        (
            df["calories_kcal"] > 5
        )
        &
        (
            df["protein_g"]
            + df["fat_g"]
            + df["carbohydrate_g"]
            > 1
        )
    ]

    # Remove very sugary foods
    df = df[
        ~(
            (df["sugar_g"] > 25)
            &
            (df["food_role"] != "fruit")
        )
    ]

    return df.reset_index(drop=True)

def optimize_quantities(
    candidates,
    target_calories,
    target_protein,
    target_fat,
    target_carbs,
):
    """
    Optimize food quantities in grams to get as close as possible
    to the target calories and macronutrients.
    """

    if candidates.empty:
        raise ValueError("No candidate foods available for optimization.")

    calories = candidates["calories_kcal"].fillna(0).to_numpy()
    protein = candidates["protein_g"].fillna(0).to_numpy()
    fat = candidates["fat_g"].fillna(0).to_numpy()
    carbs = candidates["carbohydrate_g"].fillna(0).to_numpy()

    # ---------------------------------------------------------
    # Portion bounds
    # ---------------------------------------------------------

    bounds = []

    for _, row in candidates.iterrows():

        role = row["food_role"]

        if role == "staple":
            bounds.append((0, 250))

        elif role == "protein":
            bounds.append((0, 200))

        elif role == "vegetable":
            bounds.append((0, 250))

        elif role == "fruit":
            bounds.append((0, 200))

        elif role == "healthy_fat":
            bounds.append((0, 40))

        else:
            bounds.append((0, 150))

    # ---------------------------------------------------------
    # Objective function
    # ---------------------------------------------------------

    def objective(x):

        # USDA values are per 100 g
        total_calories = np.dot(calories, x / 100)
        total_protein = np.dot(protein, x / 100)
        total_fat = np.dot(fat, x / 100)
        total_carbs = np.dot(carbs, x / 100)

        calorie_error = (
            (total_calories - target_calories)
            / max(target_calories, 1)
        )

        protein_error = (
            (total_protein - target_protein)
            / max(target_protein, 1)
        )

        fat_error = (
            (total_fat - target_fat)
            / max(target_fat, 1)
        )

        carb_error = (
            (total_carbs - target_carbs)
            / max(target_carbs, 1)
        )

        # Extra penalty when fat is below target
        fat_shortfall = (
            max(0, target_fat - total_fat)
            / max(target_fat, 1)
        )

        # Extra penalty when carbohydrates exceed target
        carb_excess = (
            max(0, total_carbs - target_carbs)
            / max(target_carbs, 1)
        )

        # Discourage unnecessarily huge portions
        portion_penalty = np.sum((x / 200) ** 2)

        return (
            15 * calorie_error ** 2
            + 8 * protein_error ** 2
            + 15 * fat_error ** 2
            + 12 * carb_error ** 2
            + 20 * fat_shortfall ** 2
            + 10 * carb_excess ** 2
            + 0.1 * portion_penalty
        )

    # ---------------------------------------------------------
    # Initial guess
    # ---------------------------------------------------------

    x0 = np.array([
        (lower + upper) / 2
        for lower, upper in bounds
    ])

    # ---------------------------------------------------------
    # Calorie constraint
    # ---------------------------------------------------------

    def calorie_constraint(x):

        total_calories = np.dot(
            calories,
            x / 100
        )

        # Allow approximately ±3% calorie deviation
        lower = target_calories * 0.97
        upper = target_calories * 1.03

        return np.array([
            total_calories - lower,
            upper - total_calories
        ])

    constraints = [
        {
            "type": "ineq",
            "fun": calorie_constraint
        }
    ]

    # ---------------------------------------------------------
    # Run optimizer
    # ---------------------------------------------------------

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={
            "maxiter": 1000,
            "ftol": 1e-7,
            "disp": False,
        },
    )

    # ---------------------------------------------------------
    # Check optimization result
    # ---------------------------------------------------------

    if not result.success:
        print(
            "Warning: optimizer did not fully converge:"
        )
        print(result.message)

    quantities = np.maximum(
        result.x,
        0
    )

    return quantities
# =========================================================
# GENERATE MEAL PLAN
# =========================================================

def generate_meal_plan(
    target_calories,
    target_protein,
    target_fat,
    target_carbs,
    diet_type="vegetarian",
):

    df = load_dataset()

    df = filter_diet(
        df,
        diet_type
    )

    df = remove_unsuitable_foods(
        df
    )

    df = add_food_roles(
        df
    )

    df = filter_nutritionally_useful_foods(
        df
    )

    candidates = select_candidates(
        df
    )

    if len(candidates) < 5:
        raise ValueError(
            "Not enough suitable foods."
        )

    quantities = optimize_quantities(
        candidates,
        target_calories,
        target_protein,
        target_fat,
        target_carbs,
    )

    candidates = candidates.copy()

    candidates["grams"] = quantities

    meal_plan = create_meal_plan(
        candidates,
        quantities
    )

    totals = calculate_meal_plan_totals(
        meal_plan
    )

    return {
        "diet_type": diet_type,

        "targets": {
            "calories": round(
                float(target_calories),
                2
            ),

            "protein_g": round(
                float(target_protein),
                2
            ),

            "fat_g": round(
                float(target_fat),
                2
            ),

            "carbs_g": round(
                float(target_carbs),
                2
            ),
        },

        "meal_plan": meal_plan,

        "totals": {
            "calories": round(
                float(totals["calories"]),
                2
            ),

            "protein_g": round(
                float(totals["protein_g"]),
                2
            ),

            "fat_g": round(
                float(totals["fat_g"]),
                2
            ),

            "carbs_g": round(
                float(totals["carbs_g"]),
                2
            ),
        },
    }

# =========================================================
# PRINT MEAL PLAN
# =========================================================

def print_meal_plan(plan):

    print()
    print("=" * 70)
    print("NUTRIGEN-AI MEAL PLAN")
    print("=" * 70)

    print("\nTARGETS")
    print("-" * 70)

    print(
        f"Calories: "
        f"{plan['targets']['calories']:.2f} kcal/day"
    )

    print(
        f"Protein:  "
        f"{plan['targets']['protein_g']:.2f} g/day"
    )

    print(
        f"Fat:      "
        f"{plan['targets']['fat_g']:.2f} g/day"
    )

    print(
        f"Carbs:    "
        f"{plan['targets']['carbs_g']:.2f} g/day"
    )

    for meal, foods in plan[
        "meal_plan"
    ].items():

        print()
        print("=" * 70)
        print(meal.upper())
        print("=" * 70)

        if not foods:

            print(
                "No foods selected."
            )

            continue

        for food in foods:

            print(
                f"{food['food']} | "
                f"{food['grams']} g | "
                f"{food['calories']} kcal | "
                f"P: {food['protein_g']} g | "
                f"F: {food['fat_g']} g | "
                f"C: {food['carbs_g']} g"
            )

    print()
    print("=" * 70)
    print("DAILY TOTAL")
    print("=" * 70)

    print(
        f"Calories: "
        f"{plan['totals']['calories']:.2f} kcal"
    )

    print(
        f"Protein:  "
        f"{plan['totals']['protein_g']:.2f} g"
    )

    print(
        f"Fat:      "
        f"{plan['totals']['fat_g']:.2f} g"
    )

    print(
        f"Carbs:    "
        f"{plan['totals']['carbs_g']:.2f} g"
    )

    print("=" * 70)


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    plan = generate_meal_plan(
        target_calories=2633.06,
        target_protein=84.0,
        target_fat=73.0,
        target_carbs=350.0,
        diet_type="vegetarian",
    )

    print_meal_plan(plan)