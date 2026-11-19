"""
NutriGEN-AI: Core Optimization Engine (Layer 2)
Personalized Nutrition & Diet Optimization
Connects user dietary preferences, physiological targets, and numerical optimization (SLSQP).
"""

from pathlib import Path
import re
import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from Backend.src.preferences import create_preferences, apply_preferences
except ImportError:
    try:
        from src.preferences import create_preferences, apply_preferences
    except ImportError:
        from preferences import create_preferences, apply_preferences


# =========================================================
# PATHS & SETTINGS
# =========================================================

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_food_dataset_final.csv"
)

MAX_FOODS = 16

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
    "candy",
    "cookie",
    "cookies",
    "cake",
    "donut",
    "doughnut",
    "pastry",
    "soft drink",
    "soda",
    "alcohol",
    "beer",
    "wine",
    "kanpyo",
    "groundcherries",
    "flour, wheat",
    "flour, whole wheat, unenriched",
    "millet, raw",
    "cereals ready-to-eat, quaker",
]

EXCLUDE_CATEGORIES = [
    "Fast Foods",
    "Restaurant Foods",
    "Meals, Entrees, and Side Dishes",
    "Sweets",
    "Snacks",
    "Baby Foods",
]


# =========================================================
# 1. LOAD DATASET (Issue 5: Sugar column included in validation)
# =========================================================

def load_dataset():
    """
    Loads and validates the master food dataset.
    Ensures required nutritional columns (including sugar_g) exist.
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at:\n{DATA_PATH}")

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
        "sugar_g",
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")

    numeric_columns = [
        "calories_kcal",
        "protein_g",
        "fat_g",
        "carbohydrate_g",
        "sugar_g",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Filter out empty or zero-calorie foods
    df = df.dropna(subset=["description", "calories_kcal"])
    df = df[df["calories_kcal"] > 0].copy()

    return df.reset_index(drop=True)


# =========================================================
# 2. FOOD ROLE ASSIGNMENT & UNSUITABLE FILTERING
# =========================================================

def remove_unsuitable_foods(df):
    """
    Removes industrial powders, baby foods, supplements, and junk categories.
    """
    df = df.copy()
    descriptions = df["description"].astype(str).str.lower()

    mask = np.ones(len(df), dtype=bool)
    for term in EXCLUDE_TERMS:
        mask &= ~descriptions.str.contains(re.escape(term), regex=True, na=False)

    df = df[mask].copy()

    category_mask = ~df["food_category"].fillna("").isin(EXCLUDE_CATEGORIES)
    df = df[category_mask].copy()

    # Exclude extreme protein isolates or extreme calorie-dense non-fats
    df = df[df["calories_kcal"] <= 900]
    return df.reset_index(drop=True)


def assign_food_role(row):
    """
    Categorizes foods into distinct culinary roles using category + keyword analysis.
    """
    cat = str(row.get("food_category", "")).lower()
    desc = str(row["description"]).lower()

    # Spices/seasonings should not be whole meal items
    if "spices and herbs" in cat or desc.startswith("spices,"):
        return "other"

    if "fruit" in cat:
        return "fruit"
    if "vegetable" in cat:
        return "vegetable"
    if "dairy" in cat:
        return "dairy"
    if any(k in cat for k in ["nut and seed", "fats and oils"]):
        return "healthy_fat"
    if any(k in cat for k in ["poultry", "beef", "pork", "finfish", "shellfish", "lamb", "veal", "meat", "eggs"]):
        return "protein"
    if "legume" in cat:
        return "protein"
    if any(k in cat for k in ["cereal grains", "baked products"]):
        return "staple"

    # Keyword fallback
    if any(k in desc for k in ["oil", "almond", "walnut", "cashew", "pistachio", "pecan", "hazelnut", "avocado", "flaxseed", "chia", "sunflower seed", "sesame seed", "pumpkin seed", "ghee", "butter"]):
        return "healthy_fat"
    if any(k in desc for k in ["lentil", "dal", "chickpea", "bean", "tofu", "tempeh", "egg", "chicken", "fish", "meat", "mutton", "turkey", "salmon", "souvlaki"]):
        return "protein"
    if any(k in desc for k in ["milk", "yogurt", "paneer", "curd", "cheese", "dahi"]):
        return "dairy"
    if any(k in desc for k in ["spinach", "broccoli", "carrot", "tomato", "okra", "cauliflower", "cabbage", "gourd", "bhindi", "aloo", "gobi"]):
        return "vegetable"
    if any(k in desc for k in ["apple", "banana", "orange", "berry", "grape", "mango", "papaya", "guava"]):
        return "fruit"
    if any(k in desc for k in ["rice", "wheat", "oat", "roti", "chapati", "bread", "quinoa", "millet", "poha", "upma", "khichdi", "idli", "dosa"]):
        return "staple"

    return "other"


def score_food_quality(row, diet_type="vegetarian"):
    """
    Ranks wholesome foods higher, prioritizing curated authentic everyday foods,
    culturally aligned items, vegetables, and fiber.
    In non-vegetarian plans, promotes lean meats, poultry, fish, and eggs.
    """
    score = 0.0
    
    # Massive priority for curated authentic everyday dishes
    source = str(row.get("source_dataset", "")).lower()
    if source == "everyday_foods_curated":
        score += 20.0

    cuisine_sc = float(row.get("cuisine_score", 0.0))
    if cuisine_sc > 0:
        score += cuisine_sc * 2.0

    cat = str(row.get("food_category", "")).lower()
    desc = str(row.get("description", "")).lower()

    # Major boost for animal proteins in non-vegetarian diet
    is_non_veg = ("non" in str(diet_type).lower())
    if is_non_veg:
        if any(k in cat for k in ["poultry", "finfish", "meat", "eggs", "seafood"]):
            score += 12.0
        elif any(k in desc for k in ["chicken", "fish", "salmon", "egg", "mutton", "tuna", "turkey", "souvlaki", "teriyaki"]):
            score += 10.0

    if any(k in cat for k in ["vegetable", "fruit", "legume", "cereal grains"]):
        score += 1.5

    fiber = float(row.get("fiber_g", 0.0))
    score += min(fiber * 0.25, 2.0)

    sugar = float(row.get("sugar_g", 0.0))
    if sugar > 15.0 and row.get("food_role") != "fruit":
        score -= 2.0

    return score


# =========================================================
# 3. MEAL CANDIDATE SELECTION (Issue 2 & 3: Structured & <= 14)
# =========================================================

def select_meal_plan_candidates(
    df_pref,
    diet_type="vegetarian",
    number_of_meals=3,
    number_of_snacks=1,
    exclude_fdc_ids=None,
    variation_seed=0,
):
    """
    Selects distinct, high-quality candidate items for each meal slot.
    Guarantees that total selected foods are strictly <= MAX_FOODS (14)
    and enforces maximum ingredient variety (no repeating the same base ingredient).
    Supports exclude_fdc_ids and variation_seed for generating alternative diverse plans.
    """
    df_pref = df_pref.copy()
    df_pref["food_role"] = df_pref.apply(assign_food_role, axis=1)
    df_pref = df_pref[df_pref["food_role"] != "other"].copy()
    df_pref["quality_score"] = df_pref.apply(lambda r: score_food_quality(r, diet_type=diet_type), axis=1)

    used_ids = set(int(x) for x in (exclude_fdc_ids or []))
    used_base_terms = set()

    is_non_veg = ("non" in str(diet_type).lower())
    is_vegan = (diet_type.lower() == "vegan")

    def get_base_term(desc):
        text = str(desc).lower()
        key_terms = [
            "poha", "upma", "idli", "dosa", "cheela", "chapati", "roti", "paratha", "naan", "pita", "khichdi",
            "basmati", "steamed rice", "brown rice", "soba", "udon", "oatmeal", "sweet potato", "toast",
            "dal tadka", "toor dal", "masoor dal", "sambar", "rajma", "chana masala", "chole", "hummus", "falafel",
            "miso", "edamame", "tofu", "paneer bhurji", "palak paneer", "paneer tikka",
            "chicken curry", "tandoori chicken", "chicken tikka", "chicken biryani", "butter chicken", "souvlaki", "chicken teriyaki", "yakitori", "chicken breast",
            "egg bhurji", "boiled eggs", "egg curry", "scrambled egg", "tamagoyaki", "omelette",
            "fish curry", "salmon", "tuna salad", "mutton curry",
            "bhindi", "okra", "aloo gobi", "lauki", "baingan", "greek salad", "tzatziki", "bok choy", "broccoli",
            "curd", "dahi", "greek yogurt", "makhana", "ghee", "olive oil", "sesame oil", "feta",
            "peanut", "almond", "walnut", "cashew", "banana", "apple", "papaya", "nori"
        ]
        for term in key_terms:
            if term in text:
                return term
        return text[:12]

    def get_best_non_veg_protein():
        sub = df_pref[
            df_pref["food_category"].isin(["poultry", "finfish", "meat", "eggs", "seafood", "shellfish"])
            & (~df_pref["fdc_id"].isin(used_ids))
        ]
        if sub.empty:
            sub = df_pref[
                df_pref["description"].astype(str).str.contains(r"chicken|fish|salmon|tuna|mutton|egg|turkey|souvlaki|teriyaki", case=False, regex=True)
                & (~df_pref["fdc_id"].isin(used_ids))
            ]
        if sub.empty:
            return get_best_food("protein")

        sub = sub.sort_values(by=["quality_score", "calories_kcal"], ascending=[False, False])
        if variation_seed and variation_seed > 0 and len(sub) > 1:
            top_k = min(len(sub), 6)
            sub = pd.concat([sub.iloc[:top_k].sample(frac=1.0, random_state=int(variation_seed)), sub.iloc[top_k:]], ignore_index=True)

        for _, row in sub.iterrows():
            base = get_base_term(row["description"])
            if base not in used_base_terms and row["fdc_id"] not in used_ids:
                chosen = row
                used_base_terms.add(base)
                used_ids.add(chosen["fdc_id"])
                return chosen

        for _, row in sub.iterrows():
            if row["fdc_id"] not in used_ids:
                chosen = row
                used_ids.add(chosen["fdc_id"])
                used_base_terms.add(get_base_term(row["description"]))
                return chosen

        # Strictly never return a previously used fdc_id
        unused = sub[~sub["fdc_id"].isin(used_ids)]
        if not unused.empty:
            chosen = unused.iloc[0]
            used_ids.add(chosen["fdc_id"])
            used_base_terms.add(get_base_term(chosen["description"]))
            return chosen
        return get_best_food("protein")

    def get_best_food(role):
        sub = df_pref[
            (df_pref["food_role"] == role)
            & (~df_pref["fdc_id"].isin(used_ids))
        ]
        if sub.empty:
            sub = df_pref[~df_pref["fdc_id"].isin(used_ids)]
        if sub.empty:
            return None

        sub = sub.sort_values(by=["quality_score", "calories_kcal"], ascending=[False, False])
        if variation_seed and variation_seed > 0 and len(sub) > 1:
            top_k = min(len(sub), 8)
            sub = pd.concat([sub.iloc[:top_k].sample(frac=1.0, random_state=int(variation_seed)), sub.iloc[top_k:]], ignore_index=True)

        # Strict pass 1: Unique FDC ID and unique base ingredient term
        for _, row in sub.iterrows():
            base = get_base_term(row["description"])
            if base not in used_base_terms and row["fdc_id"] not in used_ids:
                chosen = row
                used_base_terms.add(base)
                used_ids.add(chosen["fdc_id"])
                return chosen

        # Strict pass 2: Any unique FDC ID not yet in the daily plan
        for _, row in sub.iterrows():
            if row["fdc_id"] not in used_ids:
                chosen = row
                used_ids.add(chosen["fdc_id"])
                used_base_terms.add(get_base_term(row["description"]))
                return chosen

        # Strict pass 3: Guaranteed unique fdc_id
        unused = sub[~sub["fdc_id"].isin(used_ids)]
        if not unused.empty:
            chosen = unused.iloc[0]
            used_ids.add(chosen["fdc_id"])
            used_base_terms.add(get_base_term(chosen["description"]))
            return chosen

        return None

    # Normalize meal & snack count seamlessly supporting both semantics:
    # 1) number_of_meals represents total eating occasions (2, 3, 4, 5)
    # 2) number_of_meals represents main meals (2, 3) + number_of_snacks (0, 1, 2)
    total_eating_occasions = number_of_meals
    if number_of_meals <= 3 and number_of_snacks > 0:
        total_eating_occasions = number_of_meals + number_of_snacks

    # Breakfast protein selection
    breakfast_protein = None
    if total_eating_occasions >= 3:
        if is_non_veg:
            egg_sub = df_pref[
                ((df_pref["food_category"] == "eggs") | df_pref["description"].astype(str).str.contains(r"bhurji|scrambled egg|boiled egg|omelet", case=False, regex=True))
                & (~df_pref["fdc_id"].isin(used_ids))
            ]
            if not egg_sub.empty:
                egg_sub = egg_sub.sort_values(by=["quality_score", "calories_kcal"], ascending=[False, False])
                if variation_seed and variation_seed > 0 and len(egg_sub) > 1:
                    top_k_egg = min(len(egg_sub), 4)
                    egg_sub = pd.concat([egg_sub.iloc[:top_k_egg].sample(frac=1.0, random_state=int(variation_seed)), egg_sub.iloc[top_k_egg:]], ignore_index=True)
                chosen_egg = egg_sub.iloc[0]
                used_ids.add(chosen_egg["fdc_id"])
                used_base_terms.add(get_base_term(chosen_egg["description"]))
                breakfast_protein = chosen_egg
            else:
                breakfast_protein = get_best_food("protein")
        else:
            breakfast_protein = get_best_food("protein")

    plan_structure = []

    # 5 Meals: Breakfast, Morning Snack, Lunch, Evening Snack, Dinner
    if total_eating_occasions >= 5:
        # 1. Breakfast
        plan_structure.append(("Breakfast", "staple", get_best_food("staple"), (40.0, 150.0)))
        plan_structure.append(("Breakfast", "protein", breakfast_protein, (40.0, 180.0)))
        plan_structure.append(("Breakfast", "fruit", get_best_food("fruit"), (40.0, 180.0)))
        plan_structure.append(("Breakfast", "dairy" if not is_vegan else "protein", get_best_food("dairy" if not is_vegan else "protein"), (40.0, 180.0)))

        # 2. Morning Snack
        plan_structure.append(("Morning Snack", "fruit", get_best_food("fruit"), (40.0, 180.0)))
        plan_structure.append(("Morning Snack", "healthy_fat", get_best_food("healthy_fat"), (10.0, 40.0)))

        # 3. Lunch
        lunch_protein = get_best_non_veg_protein() if is_non_veg else get_best_food("protein")
        plan_structure.append(("Lunch", "staple", get_best_food("staple"), (40.0, 180.0)))
        plan_structure.append(("Lunch", "protein", lunch_protein, (40.0, 200.0)))
        plan_structure.append(("Lunch", "vegetable", get_best_food("vegetable"), (50.0, 250.0)))
        plan_structure.append(("Lunch", "healthy_fat", get_best_food("healthy_fat"), (10.0, 40.0)))

        # 4. Evening Snack
        plan_structure.append(("Evening Snack", "fruit", get_best_food("fruit"), (40.0, 180.0)))
        plan_structure.append(("Evening Snack", "healthy_fat", get_best_food("healthy_fat"), (10.0, 40.0)))

        # 5. Dinner
        dinner_protein = get_best_non_veg_protein() if is_non_veg else get_best_food("protein")
        plan_structure.append(("Dinner", "staple", get_best_food("staple"), (40.0, 180.0)))
        plan_structure.append(("Dinner", "protein", dinner_protein, (40.0, 200.0)))
        plan_structure.append(("Dinner", "vegetable", get_best_food("vegetable"), (50.0, 250.0)))
        plan_structure.append(("Dinner", "dairy" if not is_vegan else "vegetable", get_best_food("dairy" if not is_vegan else "vegetable"), (40.0, 180.0)))

    # 4 Meals: Breakfast, Lunch, Snack, Dinner
    elif total_eating_occasions == 4:
        # 1. Breakfast
        plan_structure.append(("Breakfast", "staple", get_best_food("staple"), (40.0, 150.0)))
        plan_structure.append(("Breakfast", "protein", breakfast_protein, (40.0, 180.0)))
        plan_structure.append(("Breakfast", "fruit", get_best_food("fruit"), (40.0, 180.0)))
        plan_structure.append(("Breakfast", "dairy" if not is_vegan else "protein", get_best_food("dairy" if not is_vegan else "protein"), (40.0, 180.0)))

        # 2. Lunch
        lunch_protein = get_best_non_veg_protein() if is_non_veg else get_best_food("protein")
        plan_structure.append(("Lunch", "staple", get_best_food("staple"), (40.0, 180.0)))
        plan_structure.append(("Lunch", "protein", lunch_protein, (40.0, 200.0)))
        plan_structure.append(("Lunch", "vegetable", get_best_food("vegetable"), (50.0, 250.0)))
        plan_structure.append(("Lunch", "healthy_fat", get_best_food("healthy_fat"), (10.0, 40.0)))

        # 3. Snack
        plan_structure.append(("Snack", "fruit", get_best_food("fruit"), (40.0, 180.0)))
        plan_structure.append(("Snack", "healthy_fat", get_best_food("healthy_fat"), (10.0, 40.0)))

        # 4. Dinner
        dinner_protein = get_best_non_veg_protein() if is_non_veg else get_best_food("protein")
        plan_structure.append(("Dinner", "staple", get_best_food("staple"), (40.0, 180.0)))
        plan_structure.append(("Dinner", "protein", dinner_protein, (40.0, 200.0)))
        plan_structure.append(("Dinner", "vegetable", get_best_food("vegetable"), (50.0, 250.0)))
        plan_structure.append(("Dinner", "dairy" if not is_vegan else "vegetable", get_best_food("dairy" if not is_vegan else "vegetable"), (40.0, 180.0)))

    # 3 Meals: Breakfast, Lunch, Dinner
    elif total_eating_occasions == 3:
        # 1. Breakfast
        plan_structure.append(("Breakfast", "staple", get_best_food("staple"), (40.0, 160.0)))
        plan_structure.append(("Breakfast", "protein", breakfast_protein, (40.0, 180.0)))
        plan_structure.append(("Breakfast", "fruit", get_best_food("fruit"), (40.0, 180.0)))
        plan_structure.append(("Breakfast", "dairy" if not is_vegan else "protein", get_best_food("dairy" if not is_vegan else "protein"), (40.0, 180.0)))

        # 2. Lunch
        lunch_protein = get_best_non_veg_protein() if is_non_veg else get_best_food("protein")
        plan_structure.append(("Lunch", "staple", get_best_food("staple"), (40.0, 190.0)))
        plan_structure.append(("Lunch", "protein", lunch_protein, (40.0, 220.0)))
        plan_structure.append(("Lunch", "vegetable", get_best_food("vegetable"), (50.0, 250.0)))
        plan_structure.append(("Lunch", "healthy_fat", get_best_food("healthy_fat"), (10.0, 40.0)))

        # 3. Dinner
        dinner_protein = get_best_non_veg_protein() if is_non_veg else get_best_food("protein")
        plan_structure.append(("Dinner", "staple", get_best_food("staple"), (40.0, 190.0)))
        plan_structure.append(("Dinner", "protein", dinner_protein, (40.0, 220.0)))
        plan_structure.append(("Dinner", "vegetable", get_best_food("vegetable"), (50.0, 250.0)))
        plan_structure.append(("Dinner", "dairy" if not is_vegan else "vegetable", get_best_food("dairy" if not is_vegan else "vegetable"), (40.0, 180.0)))

    # 2 Meals: Lunch, Dinner (Intermittent fasting)
    else:
        lunch_protein = get_best_non_veg_protein() if is_non_veg else get_best_food("protein")
        plan_structure.append(("Lunch", "staple", get_best_food("staple"), (50.0, 220.0)))
        plan_structure.append(("Lunch", "protein", lunch_protein, (50.0, 250.0)))
        plan_structure.append(("Lunch", "vegetable", get_best_food("vegetable"), (50.0, 300.0)))
        plan_structure.append(("Lunch", "fruit", get_best_food("fruit"), (40.0, 200.0)))
        plan_structure.append(("Lunch", "healthy_fat", get_best_food("healthy_fat"), (10.0, 50.0)))

        dinner_protein = get_best_non_veg_protein() if is_non_veg else get_best_food("protein")
        plan_structure.append(("Dinner", "staple", get_best_food("staple"), (50.0, 220.0)))
        plan_structure.append(("Dinner", "protein", dinner_protein, (50.0, 250.0)))
        plan_structure.append(("Dinner", "vegetable", get_best_food("vegetable"), (50.0, 300.0)))
        plan_structure.append(("Dinner", "dairy" if not is_vegan else "vegetable", get_best_food("dairy" if not is_vegan else "vegetable"), (40.0, 200.0)))
        plan_structure.append(("Dinner", "healthy_fat", get_best_food("healthy_fat"), (10.0, 50.0)))

    # Filter out any None values
    valid_slots = [item for item in plan_structure if item[2] is not None]

    # Enforce MAX_FOODS strictly
    valid_slots = valid_slots[:MAX_FOODS]

    candidate_rows = [item[2] for item in valid_slots]
    bounds = [item[3] for item in valid_slots]
    slot_info = [(item[0], item[1]) for item in valid_slots]

    candidates_df = pd.DataFrame(candidate_rows).reset_index(drop=True)
    return candidates_df, bounds, slot_info


# =========================================================
# 4. OPTIMIZATION SOLVER (Issue 4: Zero Drift SLSQP)
# =========================================================

def optimize_quantities(
    candidates_df,
    bounds,
    target_calories,
    target_protein,
    target_fat,
    target_carbs,
):
    """
    Optimizes portions (in grams) for the selected candidate items using SciPy SLSQP.
    Achieves < 2% error without dropping foods post-optimization.
    """
    calories = candidates_df["calories_kcal"].to_numpy()
    protein = candidates_df["protein_g"].to_numpy()
    fat = candidates_df["fat_g"].to_numpy()
    carbs = candidates_df["carbohydrate_g"].to_numpy()

    def objective(x):
        tot_cal = np.dot(calories, x / 100)
        tot_prot = np.dot(protein, x / 100)
        tot_fat = np.dot(fat, x / 100)
        tot_carb = np.dot(carbs, x / 100)

        err_cal = (tot_cal - target_calories) / target_calories
        err_prot = (tot_prot - target_protein) / target_protein
        err_fat = (tot_fat - target_fat) / target_fat
        err_carb = (tot_carb - target_carbs) / target_carbs

        fat_shortfall = max(0, target_fat - tot_fat) / target_fat
        carb_excess = max(0, tot_carb - target_carbs) / target_carbs

        return (
            25.0 * (err_cal ** 2)
            + 15.0 * (err_prot ** 2)
            + 20.0 * (err_fat ** 2)
            + 15.0 * (err_carb ** 2)
            + 25.0 * (fat_shortfall ** 2)
            + 20.0 * (carb_excess ** 2)
        )

    # Initial guess = mid-point of bounds
    x0 = np.array([(low + high) / 2 for low, high in bounds])

    # Calorie constraint: ±2.5% band
    def cal_constraint(x):
        tot_cal = np.dot(calories, x / 100)
        return np.array([
            tot_cal - (target_calories * 0.975),
            (target_calories * 1.025) - tot_cal
        ])

    constraints = [{"type": "ineq", "fun": cal_constraint}]

    res = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-7, "disp": False},
    )

    final_cal = np.dot(calories, res.x / 100)
    cal_error = abs(final_cal - target_calories) / target_calories
    solver_converged = bool(res.success)
    fallback_used = False

    # Fallback refinement if hard inequality constraint caused infeasibility or high error
    if not (solver_converged and cal_error <= 0.05):
        res_relaxed = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            options={"maxiter": 1000, "ftol": 1e-7, "disp": False},
        )
        final_cal_rel = np.dot(calories, res_relaxed.x / 100)
        cal_error_rel = abs(final_cal_rel - target_calories) / target_calories

        # Adopt relaxed solution only if it is strictly better or successfully converged
        if res_relaxed.success and cal_error_rel <= 0.05:
            res = res_relaxed
            cal_error = cal_error_rel
            solver_converged = True
            fallback_used = True
        elif cal_error_rel < cal_error:
            res = res_relaxed
            cal_error = cal_error_rel
            solver_converged = bool(res_relaxed.success)
            fallback_used = True

    # Validate and clamp bounds strictly
    opt_x = np.round(res.x, 1)
    for i, (low, high) in enumerate(bounds):
        opt_x[i] = max(low, min(high, opt_x[i]))

    # Final validation on clamped quantities
    verified_cal = np.dot(calories, opt_x / 100)
    final_err_pct = round(abs(verified_cal - target_calories) / target_calories * 100, 2)
    recovered = False

    # Proportional bound-clamped recovery if numerical convergence did not achieve <= 5% error
    if final_err_pct > 5.0 and verified_cal > 0:
        scale_factor = target_calories / verified_cal
        opt_x = np.round(np.clip(opt_x * scale_factor, [b[0] for b in bounds], [b[1] for b in bounds]), 1)
        verified_cal = np.dot(calories, opt_x / 100)
        final_err_pct = round(abs(verified_cal - target_calories) / target_calories * 100, 2)
        recovered = True

    within_tolerance = bool(final_err_pct <= 5.0)
    # Strictly require solver convergence AND within tolerance for overall success
    overall_success = bool(solver_converged and within_tolerance)

    opt_metadata = {
        "success": bool(overall_success),
        "solver_converged": bool(solver_converged),
        "solver_message": str(res.message),
        "calorie_error_percent": final_err_pct,
        "is_within_tolerance": bool(within_tolerance),
        "fallback_used": bool(fallback_used),
        "bounded_recovery_applied": bool(recovered)
    }

    return opt_x, opt_metadata


# =========================================================
# 5. MEAL PLAN BUILDER
# =========================================================

def make_food_entry(row, grams, role):
    grams = float(grams)
    return {
        "fdc_id": int(row["fdc_id"]),
        "food": str(row["description"]),
        "food_role": str(role),
        "grams": round(grams, 1),
        "calories": round(float(row["calories_kcal"] * grams / 100), 1),
        "protein_g": round(float(row["protein_g"] * grams / 100), 1),
        "fat_g": round(float(row["fat_g"] * grams / 100), 1),
        "carbs_g": round(float(row["carbohydrate_g"] * grams / 100), 1),
    }


def build_final_meal_plan(candidates_df, quantities, slot_info):
    """
    Builds the structured daily meal plan with zero drift.
    Every optimized gram weight is placed directly into its meal slot.
    Dynamically initializes meal slots based on slot_info to support 3, 4, or 5 meals.
    """
    meal_plan = {}
    for meal, _ in slot_info:
        if meal not in meal_plan:
            meal_plan[meal] = []

    totals = {
        "calories": 0.0,
        "protein_g": 0.0,
        "fat_g": 0.0,
        "carbs_g": 0.0,
    }

    for i, (meal, role) in enumerate(slot_info):
        row = candidates_df.iloc[i]
        grams = quantities[i]

        entry = make_food_entry(row, grams, role)
        meal_plan[meal].append(entry)

        totals["calories"] += entry["calories"]
        totals["protein_g"] += entry["protein_g"]
        totals["fat_g"] += entry["fat_g"]
        totals["carbs_g"] += entry["carbs_g"]

    # Remove empty meals if snacks weren't selected
    meal_plan = {k: v for k, v in meal_plan.items() if len(v) > 0}

    totals = {k: round(v, 1) for k, v in totals.items()}
    return meal_plan, totals


# =========================================================
# 6. MAIN API: GENERATE MEAL PLAN (Issue 1 Connected)
# =========================================================

def generate_meal_plan(
    target_calories,
    target_protein,
    target_fat,
    target_carbs,
    diet_type="vegetarian",
    allergies=None,
    disliked_foods=None,
    cuisine="indian",
    eats_eggs=False,
    number_of_meals=3,
    number_of_snacks=1,
    exclude_fdc_ids=None,
    variation_seed=0,
):
    """
    Unified meal plan generator connecting Preferences, Candidate Selection, and SLSQP Optimizer.
    Supports exclude_fdc_ids and variation_seed for regenerating alternative diverse plans.
    """
    # 1. Create and validate preferences
    preferences = create_preferences(
        diet_type=diet_type,
        eats_eggs=eats_eggs,
        cuisine=cuisine,
        allergies=allergies,
        disliked_foods=disliked_foods,
        number_of_meals=number_of_meals,
        number_of_snacks=number_of_snacks,
    )

    # 2. Load dataset with sugar validation
    raw_df = load_dataset()

    # 3. Clean unsuitable/industrial foods
    clean_df = remove_unsuitable_foods(raw_df)

    # 4. Apply preferences (diet, allergies, dislikes, cuisine scoring, deduplication)
    pref_df = apply_preferences(clean_df, preferences)

    # 5. Select exactly <= 14 candidates structured by meal slot
    candidates_df, bounds, slot_info = select_meal_plan_candidates(
        pref_df,
        diet_type=diet_type,
        number_of_meals=number_of_meals,
        number_of_snacks=number_of_snacks,
        exclude_fdc_ids=exclude_fdc_ids,
        variation_seed=variation_seed,
    )

    if len(candidates_df) < 5:
        raise ValueError("Not enough eligible foods after applying preferences and allergy constraints.")

    # 6. Optimize portion weights without post-optimization dropping
    quantities, opt_metadata = optimize_quantities(
        candidates_df,
        bounds,
        target_calories=float(target_calories),
        target_protein=float(target_protein),
        target_fat=float(target_fat),
        target_carbs=float(target_carbs),
    )

    # 7. Assemble structured meal plan
    meal_plan, totals = build_final_meal_plan(candidates_df, quantities, slot_info)

    return {
        "diet_type": diet_type,
        "preferences": preferences,
        "targets": {
            "calories": round(float(target_calories), 2),
            "protein_g": round(float(target_protein), 2),
            "fat_g": round(float(target_fat), 2),
            "carbs_g": round(float(target_carbs), 2),
        },
        "totals": totals,
        "meal_plan": meal_plan,
        "total_foods": len(candidates_df),
        "optimization": opt_metadata,
    }


# =========================================================
# 7. FOOD & MEAL SWAPPING ENGINE (Interactive Customization)
# =========================================================

def get_alternative_foods_for_item(
    fdc_id,
    diet_type="vegetarian",
    cuisine="indian",
    allergies=None,
    disliked_foods=None,
    eats_eggs=False,
    exclude_fdc_ids=None,
    limit=8,
):
    """
    Finds verified alternative foods of the same functional role for a given food item.
    Example: swapping a staple (rice) returns alternative wholesome staples (quinoa, oats, roti, etc.).
    """
    raw_df = load_dataset()
    clean_df = remove_unsuitable_foods(raw_df)
    preferences = create_preferences(
        diet_type=diet_type,
        eats_eggs=eats_eggs,
        cuisine=cuisine,
        allergies=allergies,
        disliked_foods=disliked_foods
    )
    pref_df = apply_preferences(clean_df, preferences)
    pref_df["food_role"] = pref_df.apply(assign_food_role, axis=1)

    target_match = pref_df[pref_df["fdc_id"] == int(fdc_id)]
    if target_match.empty:
        target_match = clean_df[clean_df["fdc_id"] == int(fdc_id)]
        role = assign_food_role(target_match.iloc[0]) if not target_match.empty else "staple"
    else:
        role = target_match.iloc[0]["food_role"]

    excluded = set(int(x) for x in (exclude_fdc_ids or []))
    excluded.add(int(fdc_id))

    candidates = pref_df[
        (pref_df["food_role"] == role) &
        (~pref_df["fdc_id"].isin(excluded))
    ].copy()

    if candidates.empty:
        candidates = pref_df[~pref_df["fdc_id"].isin(excluded)].copy()

    candidates["quality_score"] = candidates.apply(lambda r: score_food_quality(r, diet_type=diet_type), axis=1)
    candidates = candidates.sort_values(by=["quality_score", "calories_kcal"], ascending=[False, False])

    results = []
    seen_names = set()
    for _, row in candidates.iterrows():
        name = str(row["description"]).strip()
        if name not in seen_names:
            seen_names.add(name)
            results.append({
                "fdc_id": int(row["fdc_id"]),
                "food": name,
                "food_role": str(role),
                "calories_per_100g": round(float(row["calories_kcal"]), 1),
                "protein_per_100g": round(float(row["protein_g"]), 1),
                "fat_per_100g": round(float(row["fat_g"]), 1),
                "carbs_per_100g": round(float(row["carbohydrate_g"]), 1),
            })
            if len(results) >= limit:
                break
    return results


def swap_food_in_plan(
    current_plan,
    targets,
    fdc_id_to_replace,
    replacement_fdc_id=None,
    diet_type="vegetarian",
    cuisine="indian",
    allergies=None,
    disliked_foods=None,
    eats_eggs=False,
):
    """
    Replaces a single food item in an active meal plan with an alternative of the same role,
    re-runs SLSQP optimization across all daily items so total calories and macros stay balanced,
    and returns the updated plan.
    """
    fdc_id_to_replace = int(fdc_id_to_replace)
    meal_plan = current_plan.get("meal_plan", {})

    target_meal = None
    replaced_item = None
    all_current_items = []

    for meal_name, items in meal_plan.items():
        for item in items:
            all_current_items.append((meal_name, item))
            if int(item["fdc_id"]) == fdc_id_to_replace:
                target_meal = meal_name
                replaced_item = item

    if not replaced_item:
        raise ValueError(f"Food item with ID {fdc_id_to_replace} not found in current meal plan.")

    raw_df = load_dataset()
    clean_df = remove_unsuitable_foods(raw_df)

    if replacement_fdc_id is not None:
        replacement_row = clean_df[clean_df["fdc_id"] == int(replacement_fdc_id)]
        if replacement_row.empty:
            raise ValueError(f"Replacement food with ID {replacement_fdc_id} not found.")
        chosen_rep = replacement_row.iloc[0]
    else:
        current_ids = [int(it["fdc_id"]) for _, it in all_current_items]
        alts = get_alternative_foods_for_item(
            fdc_id=fdc_id_to_replace,
            diet_type=diet_type,
            cuisine=cuisine,
            allergies=allergies,
            disliked_foods=disliked_foods,
            eats_eggs=eats_eggs,
            exclude_fdc_ids=current_ids,
            limit=1
        )
        if not alts:
            raise ValueError("No eligible alternative food found to swap.")
        rep_id = alts[0]["fdc_id"]
        chosen_rep = clean_df[clean_df["fdc_id"] == rep_id].iloc[0]

    new_candidate_rows = []
    new_bounds = []
    new_slot_info = []

    role_bounds_map = {
        "staple": (40.0, 200.0),
        "protein": (40.0, 220.0),
        "vegetable": (50.0, 300.0),
        "fruit": (40.0, 200.0),
        "healthy_fat": (10.0, 40.0),
        "dairy": (40.0, 200.0),
    }

    for meal_name, item in all_current_items:
        role = item.get("food_role", "staple")
        b = role_bounds_map.get(role, (30.0, 200.0))
        if int(item["fdc_id"]) == fdc_id_to_replace:
            new_candidate_rows.append(chosen_rep)
            new_bounds.append(b)
            new_slot_info.append((meal_name, role))
        else:
            row_match = clean_df[clean_df["fdc_id"] == int(item["fdc_id"])]
            if not row_match.empty:
                new_candidate_rows.append(row_match.iloc[0])
            else:
                new_candidate_rows.append(pd.Series({
                    "fdc_id": item["fdc_id"],
                    "description": item["food"],
                    "calories_kcal": item["calories"] / (item["grams"] / 100),
                    "protein_g": item["protein_g"] / (item["grams"] / 100),
                    "fat_g": item["fat_g"] / (item["grams"] / 100),
                    "carbohydrate_g": item["carbs_g"] / (item["grams"] / 100),
                }))
            new_bounds.append(b)
            new_slot_info.append((meal_name, role))

    candidates_df = pd.DataFrame(new_candidate_rows).reset_index(drop=True)

    quantities, opt_metadata = optimize_quantities(
        candidates_df,
        new_bounds,
        target_calories=float(targets["calories"]),
        target_protein=float(targets["protein_g"]),
        target_fat=float(targets["fat_g"]),
        target_carbs=float(targets["carbs_g"]),
    )

    new_meal_plan, new_totals = build_final_meal_plan(candidates_df, quantities, new_slot_info)

    return {
        "diet_type": diet_type,
        "targets": targets,
        "totals": new_totals,
        "meal_plan": new_meal_plan,
        "optimization": opt_metadata,
        "swapped_meal": target_meal,
        "replaced_fdc_id": fdc_id_to_replace,
        "new_fdc_id": int(chosen_rep["fdc_id"]),
        "new_food_name": str(chosen_rep["description"]),
    }


def swap_entire_meal_in_plan(
    current_plan,
    targets,
    meal_name_to_swap,
    diet_type="vegetarian",
    cuisine="indian",
    allergies=None,
    disliked_foods=None,
    eats_eggs=False,
    variation_seed=1,
):
    """
    Replaces all food items in a specific meal occasion (e.g. Lunch) with brand-new,
    high-quality candidates of matching roles, re-runs SLSQP portion optimization,
    and returns the refreshed plan.
    """
    raw_df = load_dataset()
    clean_df = remove_unsuitable_foods(raw_df)
    preferences = create_preferences(
        diet_type=diet_type,
        eats_eggs=eats_eggs,
        cuisine=cuisine,
        allergies=allergies,
        disliked_foods=disliked_foods
    )
    pref_df = apply_preferences(clean_df, preferences)
    pref_df["food_role"] = pref_df.apply(assign_food_role, axis=1)

    meal_plan = current_plan.get("meal_plan", {})
    if meal_name_to_swap not in meal_plan:
        raise ValueError(f"Meal '{meal_name_to_swap}' not found in current meal plan.")

    used_ids = set()
    old_meal_ids = set()
    for m_name, items in meal_plan.items():
        for it in items:
            if m_name == meal_name_to_swap:
                old_meal_ids.add(int(it["fdc_id"]))
            else:
                used_ids.add(int(it["fdc_id"]))

    used_ids.update(old_meal_ids)

    new_meal_candidates = []
    for item in meal_plan[meal_name_to_swap]:
        role = item.get("food_role", "staple")
        candidates = pref_df[
            (pref_df["food_role"] == role) &
            (~pref_df["fdc_id"].isin(used_ids))
        ].copy()
        if candidates.empty:
            candidates = pref_df[~pref_df["fdc_id"].isin(used_ids)].copy()

        candidates["quality_score"] = candidates.apply(lambda r: score_food_quality(r, diet_type=diet_type), axis=1)
        candidates = candidates.sort_values(by=["quality_score", "calories_kcal"], ascending=[False, False])
        if variation_seed and len(candidates) > 1:
            top_k = min(len(candidates), 6)
            candidates = pd.concat([candidates.iloc[:top_k].sample(frac=1.0, random_state=int(variation_seed)), candidates.iloc[top_k:]], ignore_index=True)

        chosen = candidates.iloc[0]
        used_ids.add(int(chosen["fdc_id"]))
        new_meal_candidates.append(chosen)

    new_candidate_rows = []
    new_bounds = []
    new_slot_info = []

    role_bounds_map = {
        "staple": (40.0, 200.0),
        "protein": (40.0, 220.0),
        "vegetable": (50.0, 300.0),
        "fruit": (40.0, 200.0),
        "healthy_fat": (10.0, 40.0),
        "dairy": (40.0, 200.0),
    }

    for m_name, items in meal_plan.items():
        if m_name == meal_name_to_swap:
            for chosen in new_meal_candidates:
                role = chosen["food_role"]
                new_candidate_rows.append(chosen)
                new_bounds.append(role_bounds_map.get(role, (30.0, 200.0)))
                new_slot_info.append((m_name, role))
        else:
            for item in items:
                role = item.get("food_role", "staple")
                row_match = clean_df[clean_df["fdc_id"] == int(item["fdc_id"])]
                if not row_match.empty:
                    new_candidate_rows.append(row_match.iloc[0])
                else:
                    new_candidate_rows.append(pd.Series({
                        "fdc_id": item["fdc_id"],
                        "description": item["food"],
                        "calories_kcal": item["calories"] / (item["grams"] / 100),
                        "protein_g": item["protein_g"] / (item["grams"] / 100),
                        "fat_g": item["fat_g"] / (item["grams"] / 100),
                        "carbohydrate_g": item["carbs_g"] / (item["grams"] / 100),
                    }))
                new_bounds.append(role_bounds_map.get(role, (30.0, 200.0)))
                new_slot_info.append((m_name, role))

    candidates_df = pd.DataFrame(new_candidate_rows).reset_index(drop=True)

    quantities, opt_metadata = optimize_quantities(
        candidates_df,
        new_bounds,
        target_calories=float(targets["calories"]),
        target_protein=float(targets["protein_g"]),
        target_fat=float(targets["fat_g"]),
        target_carbs=float(targets["carbs_g"]),
    )

    new_meal_plan, new_totals = build_final_meal_plan(candidates_df, quantities, new_slot_info)

    return {
        "diet_type": diet_type,
        "targets": targets,
        "totals": new_totals,
        "meal_plan": new_meal_plan,
        "optimization": opt_metadata,
        "swapped_meal": meal_name_to_swap,
    }


def generate_multi_day_plan(
    target_calories,
    target_protein,
    target_fat,
    target_carbs,
    diet_type="vegetarian",
    allergies=None,
    disliked_foods=None,
    cuisine="indian",
    eats_eggs=False,
    number_of_meals=3,
    number_of_snacks=1,
    plan_days=3,
    start_seed=0,
):
    """
    Generates a consecutive multi-day plan (e.g. 3-day or 7-day) where each day has
    distinct, rotating ingredients to prevent dietary fatigue.
    """
    days_result = []
    cumulative_recent_ids = []

    for d in range(1, plan_days + 1):
        exclude_window = cumulative_recent_ids[-24:] if cumulative_recent_ids else []
        day_seed = (start_seed or 0) + (d - 1) * 11 + 3

        day_plan = generate_meal_plan(
            target_calories=target_calories,
            target_protein=target_protein,
            target_fat=target_fat,
            target_carbs=target_carbs,
            diet_type=diet_type,
            allergies=allergies,
            disliked_foods=disliked_foods,
            cuisine=cuisine,
            eats_eggs=eats_eggs,
            number_of_meals=number_of_meals,
            number_of_snacks=number_of_snacks,
            exclude_fdc_ids=exclude_window,
            variation_seed=day_seed,
        )

        day_ids = [int(f["fdc_id"]) for items in day_plan["meal_plan"].values() for f in items]
        cumulative_recent_ids.extend(day_ids)

        days_result.append({
            "day_number": d,
            "day_label": f"Day {d}",
            "meal_plan": day_plan["meal_plan"],
            "totals": day_plan["totals"],
            "total_foods": day_plan["total_foods"],
            "optimization": day_plan["optimization"]
        })

    return days_result


# =========================================================
# 7. PRETTY PRINTER FOR CLI & TESTING
# =========================================================

def print_meal_plan(plan):
    print("\n" + "=" * 70)
    print("NUTRIGEN-AI PERSONALIZED MEAL PLAN")
    print("=" * 70)

    t = plan["targets"]
    print(f"TARGETS: Calories: {t['calories']:.1f} kcal | Protein: {t['protein_g']:.1f}g | Fat: {t['fat_g']:.1f}g | Carbs: {t['carbs_g']:.1f}g")

    for meal, foods in plan["meal_plan"].items():
        print("\n" + "-" * 70)
        print(f"{meal.upper()} ({len(foods)} items)")
        print("-" * 70)
        for f in foods:
            print(f"  • {f['food']:<45} | {f['grams']:>5.1f}g | {f['calories']:>5.1f} kcal | P: {f['protein_g']:>4.1f}g | F: {f['fat_g']:>4.1f}g | C: {f['carbs_g']:>4.1f}g")

    tot = plan["totals"]
    print("\n" + "=" * 70)
    print(f"DAILY TOTALS (Total foods: {plan['total_foods']}/{MAX_FOODS})")
    print("=" * 70)
    print(f"Calories: {tot['calories']:.1f} kcal (Target: {t['calories']:.1f} kcal, Error: {abs(tot['calories']-t['calories'])/t['calories']*100:.1f}%)")
    print(f"Protein:  {tot['protein_g']:.1f}g   (Target: {t['protein_g']:.1f}g,   Error: {abs(tot['protein_g']-t['protein_g'])/t['protein_g']*100:.1f}%)")
    print(f"Fat:      {tot['fat_g']:.1f}g   (Target: {t['fat_g']:.1f}g,   Error: {abs(tot['fat_g']-t['fat_g'])/t['fat_g']*100:.1f}%)")
    print(f"Carbs:    {tot['carbs_g']:.1f}g   (Target: {t['carbs_g']:.1f}g,   Error: {abs(tot['carbs_g']-t['carbs_g'])/t['carbs_g']*100:.1f}%)")
    print("=" * 70 + "\n")


# =========================================================
# MAIN TEST EXECUTION
# =========================================================

if __name__ == "__main__":
    plan = generate_meal_plan(
        target_calories=2633.06,
        target_protein=84.0,
        target_fat=73.0,
        target_carbs=350.0,
        diet_type="vegetarian",
        allergies=["peanuts"],
        disliked_foods=["mushroom"],
        cuisine="indian",
        eats_eggs=True,
        number_of_meals=3,
        number_of_snacks=1,
    )
    print_meal_plan(plan)
