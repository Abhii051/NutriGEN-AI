# ============================================================
# NUTRIGEN-AI
# AI / Nutrition Requirement Module
# BMR -> TDEE -> Calorie Target -> Macronutrients
# ============================================================


# ------------------------------------------------------------
# 1. BMR CALCULATION
# ------------------------------------------------------------

def calculate_bmr(age, weight_kg, height_cm, sex):
    """
    Calculate Basal Metabolic Rate (BMR)
    using the Mifflin-St Jeor equation.
    """

    if age <= 0:
        raise ValueError("Age must be greater than 0.")

    if weight_kg <= 0:
        raise ValueError("Weight must be greater than 0.")

    if height_cm <= 0:
        raise ValueError("Height must be greater than 0.")

    sex = sex.lower()

    if sex == "male":
        bmr = (
            (10 * weight_kg)
            + (6.25 * height_cm)
            - (5 * age)
            + 5
        )

    elif sex == "female":
        bmr = (
            (10 * weight_kg)
            + (6.25 * height_cm)
            - (5 * age)
            - 161
        )

    else:
        raise ValueError(
            "Sex must be 'male' or 'female'."
        )

    return round(bmr, 2)


# ------------------------------------------------------------
# 2. TDEE CALCULATION
# ------------------------------------------------------------

def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure (TDEE)
    using an activity multiplier.
    """

    activity_factors = {
        "sedentary": 1.20,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
        "extremely_active": 1.90
    }

    activity_level = activity_level.lower()

    if activity_level not in activity_factors:
        raise ValueError(
            "Invalid activity level.\n"
            "Choose from: sedentary, light, moderate, "
            "very_active, extremely_active."
        )

    tdee = bmr * activity_factors[activity_level]

    return round(tdee, 2)


# ------------------------------------------------------------
# 3. CALORIE TARGET
# ------------------------------------------------------------

def calculate_calorie_target(tdee, goal):
    """
    Calculate a prototype daily calorie target
    based on the selected goal.

    These percentages are software-prototype assumptions
    and should not be treated as universal nutrition advice.
    """

    goal = goal.lower()

    if goal == "weight_loss":

        calorie_target = tdee * 0.90

    elif goal == "maintenance":

        calorie_target = tdee

    elif goal == "weight_gain":

        calorie_target = tdee * 1.10

    else:

        raise ValueError(
            "Invalid goal.\n"
            "Choose from: weight_loss, maintenance, weight_gain."
        )

    return round(calorie_target, 2)


# ------------------------------------------------------------
# 4. MACRONUTRIENT CALCULATION
# ------------------------------------------------------------

def calculate_macros(
    calorie_target,
    weight_kg,
    protein_per_kg=1.2,
    fat_percentage=0.25
):
    """
    Calculate prototype macronutrient targets.

    Protein:
        protein_per_kg * body weight

    Fat:
        fat_percentage of total calories

    Carbohydrates:
        Remaining calories after protein and fat

    Energy values:
        Protein = 4 kcal/g
        Carbohydrates = 4 kcal/g
        Fat = 9 kcal/g

    The default values are placeholders for software testing.
    """

    if calorie_target <= 0:
        raise ValueError(
            "Calorie target must be greater than 0."
        )

    if weight_kg <= 0:
        raise ValueError(
            "Weight must be greater than 0."
        )

    if protein_per_kg <= 0:
        raise ValueError(
            "Protein per kg must be greater than 0."
        )

    if not 0 < fat_percentage < 1:
        raise ValueError(
            "Fat percentage must be between 0 and 1."
        )

    # Protein
    protein_g = weight_kg * protein_per_kg
    protein_calories = protein_g * 4

    # Fat
    fat_calories = calorie_target * fat_percentage
    fat_g = fat_calories / 9

    # Carbohydrates
    remaining_calories = (
        calorie_target
        - protein_calories
        - fat_calories
    )

    if remaining_calories < 0:
        raise ValueError(
            "Protein and fat settings require more calories "
            "than the available calorie target."
        )

    carbs_g = remaining_calories / 4

    return {
        "protein_g": round(protein_g, 2),
        "fat_g": round(fat_g, 2),
        "carbs_g": round(carbs_g, 2)
    }


# ------------------------------------------------------------
# 5. COMPLETE NUTRITION PROFILE
# ------------------------------------------------------------

def generate_nutrition_profile(
    age,
    weight_kg,
    height_cm,
    sex,
    activity_level,
    goal
):
    """
    Run the complete NUTRIGEN-AI nutrition calculation pipeline.

    Input:
        User information

    Output:
        BMR
        TDEE
        Calorie target
        Macronutrients
    """

    # Step 1: BMR
    bmr = calculate_bmr(
        age,
        weight_kg,
        height_cm,
        sex
    )

    # Step 2: TDEE
    tdee = calculate_tdee(
        bmr,
        activity_level
    )

    # Step 3: Calorie target
    calorie_target = calculate_calorie_target(
        tdee,
        goal
    )

    # Step 4: Macronutrients
    macros = calculate_macros(
        calorie_target,
        weight_kg
    )

    # Combine everything into one dictionary
    profile = {
        "age": age,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "sex": sex,
        "activity_level": activity_level,
        "goal": goal,

        "bmr": bmr,
        "tdee": tdee,
        "calorie_target": calorie_target,

        "protein_g": macros["protein_g"],
        "fat_g": macros["fat_g"],
        "carbs_g": macros["carbs_g"]
    }

    return profile


# ------------------------------------------------------------
# 6. TEST THE COMPLETE MODULE
# ------------------------------------------------------------

if __name__ == "__main__":

    # --------------------------------------------------------
    # SAMPLE USER
    # --------------------------------------------------------
    # This is a synthetic adult test profile for development.
    # Do not use these values as personal nutrition advice.

    age = 20
    weight_kg = 70
    height_cm = 175

    sex = "male"

    activity_level = "moderate"

    goal = "weight_loss"


    # --------------------------------------------------------
    # RUN COMPLETE NUTRITION PIPELINE
    # --------------------------------------------------------

    profile = generate_nutrition_profile(
        age=age,
        weight_kg=weight_kg,
        height_cm=height_cm,
        sex=sex,
        activity_level=activity_level,
        goal=goal
    )


    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    print("\n======================================")
    print("          NUTRIGEN-AI")
    print("     Nutrition Requirement Engine")
    print("======================================")

    print("\nUSER INFORMATION")
    print("--------------------------------------")

    print("Age:", profile["age"])
    print("Weight:", profile["weight_kg"], "kg")
    print("Height:", profile["height_cm"], "cm")
    print("Sex:", profile["sex"])
    print("Activity Level:", profile["activity_level"])
    print("Goal:", profile["goal"])


    print("\nENERGY CALCULATIONS")
    print("--------------------------------------")

    print("BMR:", profile["bmr"], "kcal/day")
    print("TDEE:", profile["tdee"], "kcal/day")
    print(
        "Calorie Target:",
        profile["calorie_target"],
        "kcal/day"
    )


    print("\nMACRONUTRIENTS")
    print("--------------------------------------")

    print(
        "Protein:",
        profile["protein_g"],
        "g/day"
    )

    print(
        "Fat:",
        profile["fat_g"],
        "g/day"
    )

    print(
        "Carbohydrates:",
        profile["carbs_g"],
        "g/day"
    )


    print("\n======================================")
    print("Nutrition profile generated successfully.")
    print("======================================\n")