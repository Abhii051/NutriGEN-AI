
import pandas as pd
import joblib
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load datasets
train = pd.read_csv("data/processed/foods_train.csv")
test = pd.read_csv("data/processed/foods_test.csv")

# Separate features and target
target = "food_type"

X_train = train.drop(columns=[target])
y_train = train[target]

X_test = test.drop(columns=[target])
y_test = test[target]

# Correct column names
text_column = "food_name"

numeric_columns = [
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "fiber_g"
]

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "text",
            TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                strip_accents="unicode"
            ),
            text_column
        ),
        (
            "numeric",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]),
            numeric_columns
        )
    ]
)

# Build model
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ))
])

# Train
print("Training model...")
model.fit(X_train, y_train)

# Predict
print("Evaluating model...")
y_pred = model.predict(X_test)

# Evaluation
print("\nAccuracy:", accuracy_score(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model
os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/food_classifier.pkl")

print("\nModel saved to models/food_classifier.pkl")