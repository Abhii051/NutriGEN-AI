def calculate_bmr(weight, height, age, gender):
    if gender.lower() == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161


def calculate_tdee(bmr, activity_level):
    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    return bmr * activity_factors[activity_level]


def calculate_calories(tdee, goal):
    if goal == "gain":
        return tdee + 300
    elif goal == "lose":
        return tdee - 300
    else:
        return tdee