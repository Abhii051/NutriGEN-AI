
import pandas as pd
import joblib

from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

train_file = DATA_DIR / "foods_train.csv"
test_file = DATA_DIR / "foods_test.csv"

train_df = pd.read_csv(train_file)
test_df = pd.read_csv(test_file)

text_feature = "food_name"

numeric_features = [
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "fiber_g"
]

target = "food_type_final"

X_train = train_df[[text_feature] + numeric_features]
y_train = train_df[target]

X_test = test_df[[text_feature] + numeric_features]
y_test = test_df[target]

# Text processing
text_transformer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    strip_accents="unicode"
)

# Numeric preprocessing
numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

preprocessor = ColumnTransformer([
    ("text", text_transformer, text_feature),
    ("numeric", numeric_transformer, numeric_features)
])

# Classifier
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ))
])

print("Training classifier...")

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\nTest Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

model_path = MODEL_DIR / "food_classifier.pkl"

joblib.dump(model, model_path)

print("\nModel saved to:")
print(model_path)