
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "foods_final_training.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

df = pd.read_csv(INPUT_FILE)

# Features and target
X = df[
    [
        "food_name",
        "calories",
        "protein_g",
        "fat_g",
        "carbs_g",
        "fiber_g"
    ]
]

y = df["food_type_final"]

# Stratified 80/20 split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

train_df = X_train.copy()
train_df["food_type_final"] = y_train

test_df = X_test.copy()
test_df["food_type_final"] = y_test

train_file = OUTPUT_DIR / "foods_train.csv"
test_file = OUTPUT_DIR / "foods_test.csv"

train_df.to_csv(train_file, index=False)
test_df.to_csv(test_file, index=False)

print("Total records:", len(df))
print("Training records:", len(train_df))
print("Testing records:", len(test_df))

print("\nTraining class counts:")
print(y_train.value_counts())

print("\nTesting class counts:")
print(y_test.value_counts())

print("\nSaved:")
print(train_file)
print(test_file)