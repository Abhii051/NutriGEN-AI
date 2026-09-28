import joblib
import pandas as pd

# Load trained model
model = joblib.load("models/food_classifier.pkl")

print("NutriGEN-AI Food Classifier")
print("Type 'exit' to quit.")

while True:
    food_name = input("\nEnter food name: ").strip()

    if food_name.lower() == "exit":
        break

    if not food_name:
        print("Please enter a food name.")
        continue

    # Create input with the same columns used during training
    food = pd.DataFrame([{
        "food_id": 0,
        "food_name": food_name,
        "source": "user_input",
        "protein_g": 0,
        "fat_g": 0,
        "carbs_g": 0,
        "fiber_g": 0,
        "calories": 0
    }])

    prediction = model.predict(food)[0]

    print("Predicted category:", prediction)