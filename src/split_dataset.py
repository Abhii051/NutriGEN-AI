import pandas as pd
from sklearn.model_selection import train_test_split

# Load the classified dataset
df = pd.read_csv("data/processed/foods_for_training.csv")

# Features and labels
X = df.drop(columns=["food_type"])
y = df["food_type"]

# Split: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Save the datasets
train = X_train.copy()
train["food_type"] = y_train

test = X_test.copy()
test["food_type"] = y_test

train.to_csv("data/processed/foods_train.csv", index=False)
test.to_csv("data/processed/foods_test.csv", index=False)

print("Training records:", len(train))
print("Testing records:", len(test))

print("\nTraining class distribution:")
print(train["food_type"].value_counts())

print("\nTesting class distribution:")
print(test["food_type"].value_counts())

print("\nDataset split completed!")