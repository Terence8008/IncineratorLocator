import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

df = pd.read_csv("data/selangor_sample_points_full.csv")

# ===============================
# Select Features for Training
# ===============================
# Use MCDA-weighted normalized features + land use score
feature_cols = [
    "population_norm",
    "dist_river_norm",
    "dist_road_norm",
    "landuse_score"
]

X = df[feature_cols]
y = df["suitable"]

# ===============================
# Train-Test Split
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, shuffle=True
)

# ===============================
# Train Random Forest Model
# ===============================
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42
)

rf.fit(X_train, y_train)

# ===============================
# Evaluation
# ===============================
y_pred = rf.predict(X_test)

print("\n Model Performance")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ===============================
# Save Trained Model
# ===============================
joblib.dump(rf, "models/incinerator_rf_model.pkl")
print("\n Model saved to model/incinerator_rf_model.pkl")