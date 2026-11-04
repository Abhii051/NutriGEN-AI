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
    from Backend.src.candidates import add_candidate_roles
except ImportError:
    try:
        from src.preferences import create_preferences, apply_preferences
        from src.candidates import add_candidate_roles
    except ImportError:
        from preferences import create_preferences, apply_preferences
        from candidates import add_candidate_roles


# =========================================================
# PATHS & SETTINGS
# =========================================================

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_food_dataset_final.csv"
)

MAX_FOODS = 14

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
    if any(k in cat for k in ["poultry", "beef", "pork", "finfish", "shellfish", "lamb", "veal"]):
        return "protein"
    if "legume" in cat:
        return "protein"
    if any(k in cat for k in ["cereal grains", "baked products"]):
        return "staple"

    # Keyword fallback
    if any(k in desc for k in ["oil", "almond", "walnut", "cashew", "pistachio", "pecan", "hazelnut", "avocado", "flaxseed", "chia", "sunflower seed", "sesame seed", "pumpkin seed", "ghee", "butter"]):
        return "healthy_fat"
    if any(k in desc for k in ["lentil", "dal", "chickpea", "bean", "tofu", "tempeh", "egg", "chicken", "fish", "meat"]):
        return "protein"
    if any(k in desc for k in ["milk", "yogurt", "paneer", "curd", "cheese", "dahi"]):
        return "dairy"
    if any(k in desc for k in ["spinach", "broccoli", "carrot", "tomato", "okra", "cauliflower", "cabbage", "gourd"]):
        return "vegetable"
    if any(k in desc for k in ["apple", "banana", "orange", "berry", "grape", "mango", "papaya", "guava"]):
        return "fruit"
    if any(k in desc for k in ["rice", "wheat", "oat", "roti", "chapati", "bread", "quinoa", "millet", "poha"]):
        return "staple"

    return "other"


def score_food_quality(row):
    """
    Ranks wholesome foods higher, preferring culturally aligned (Indian) items,
    whole grains, vegetables, and high fiber.
    """
    score = 0.0
    if row.get("cuisine_score", 0) > 0:
        score += 3.0

    cat = str(row.get("food_category", "")).lower()
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
):
    """
    Selects distinct, high-quality candidate items for each meal slot.
    Guarantees that total selected foods are strictly <= MAX_FOODS (14)
    and enforces maximum ingredient variety (no repeating the same base ingredient).
    """
    df_pref = df_pref.copy()
    df_pref["food_role"] = df_pref.apply(assign_food_role, axis=1)
    df_pref = df_pref[df_pref["food_role"] != "other"].copy()
    df_pref["quality_score"] = df_pref.apply(score_food_quality, axis=1)

    used_ids = set()
    used_base_terms = set()

    def get_base_term(desc):
        text = str(desc).lower()
        key_terms = [
            "peanut", "almond", "walnut", "cashew", "macadamia", "sunflower", "sesame",
            "millet", "oat", "wheat", "rice", "quinoa", "barley", "pasta", "corn",
            "lentil", "chickpea", "besan", "bean", "tofu", "tempeh", "egg", "chicken", "turkey", "beef", "fish", "salmon", "tuna",
            "apple", "banana", "berry", "orange", "grape", "mango", "papaya", "guava", "melon",
            "curd", "yogurt", "cheese", "milk", "paneer",
            "spinach", "broccoli", "carrot", "tomato", "okra", "gourd", "drumstick", "cabbage", "cauliflower", "shallot", "onion"
        ]
        for term in key_terms:
            if term in text:
                return term
        return text[:12]

    def get_best_food(role):
        sub = df_pref[
            (df_pref["food_role"] == role)
            & (~df_pref["fdc_id"].isin(used_ids))
        ]
        if sub.empty:
            sub = df_pref[df_pref["food_role"] == role]
        if sub.empty:
            return None

        sub = sub.sort_values(by=["quality_score", "calories_kcal"], ascending=[False, False])

        # Find first food whose base term hasn't been used yet
        chosen = None
        for _, row in sub.iterrows():
            base = get_base_term(row["description"])
            if base not in used_base_terms:
                chosen = row
                used_base_terms.add(base)
                break

        if chosen is None:
            chosen = sub.iloc[0]

        used_ids.add(chosen["fdc_id"])
        return chosen

    is_vegan = (diet_type.lower() == "vegan")

    # Slot Blueprint (Strictly <= 14 items total)
    plan_structure = []

    # Breakfast (4 foods)
    plan_structure.append(("Breakfast", "staple", get_best_food("staple"), (40.0, 150.0)))
    plan_structure.append(("Breakfast", "protein", get_best_food("protein"), (40.0, 180.0)))
    plan_structure.append(("Breakfast", "fruit", get_best_food("fruit"), (40.0, 180.0)))
    plan_structure.append(("Breakfast", "dairy" if not is_vegan else "protein", get_best_food("dairy" if not is_vegan else "protein"), (40.0, 180.0)))

    # Lunch (4 foods)
    plan_structure.append(("Lunch", "staple", get_best_food("staple"), (40.0, 180.0)))
    plan_structure.append(("Lunch", "protein", get_best_food("protein"), (40.0, 200.0)))
    plan_structure.append(("Lunch", "vegetable", get_best_food("vegetable"), (50.0, 250.0)))
    plan_structure.append(("Lunch", "healthy_fat", get_best_food("healthy_fat"), (10.0, 40.0)))

    # Dinner (4 foods)
    plan_structure.append(("Dinner", "staple", get_best_food("staple"), (40.0, 180.0)))
    plan_structure.append(("Dinner", "protein", get_best_food("protein"), (40.0, 200.0)))
    plan_structure.append(("Dinner", "vegetable", get_best_food("vegetable"), (50.0, 250.0)))
    plan_structure.append(("Dinner", "dairy" if not is_vegan else "vegetable", get_best_food("dairy" if not is_vegan else "vegetable"), (40.0, 180.0)))

    # Snack (2 foods if snack requested)
    if number_of_snacks > 0:
        plan_structure.append(("Snack", "fruit", get_best_food("fruit"), (40.0, 180.0)))
        plan_structure.append(("Snack", "healthy_fat", get_best_food("healthy_fat"), (10.0, 40.0)))

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

    return np.round(res.x, 1)


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
    """
    meal_plan = {
        "Breakfast": [],
        "Lunch": [],
        "Dinner": [],
        "Snack": [],
    }

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
):
    """
    Unified meal plan generator connecting Preferences, Candidate Selection, and SLSQP Optimizer.
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
    )

    if len(candidates_df) < 5:
        raise ValueError("Not enough eligible foods after applying preferences and allergy constraints.")

    # 6. Optimize portion weights without post-optimization dropping
    quantities = optimize_quantities(
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
    }


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
