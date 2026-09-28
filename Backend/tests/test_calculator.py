from nutrition.src.calculator import calculate_bmr, calculate_tdee, calculate_calories


weight = 55
height = 168
age = 18
gender = "male"

bmr = calculate_bmr(weight, height, age, gender)
print("BMR:", round(bmr, 2))

tdee = calculate_tdee(bmr, "moderate")
print("TDEE:", round(tdee, 2))

calories = calculate_calories(tdee, "gain")
print("Calories for weight gain:", round(calories, 2))