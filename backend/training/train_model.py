import pandas as pd
import matplotlib.pyplot as plt
import joblib
import seaborn as sns
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, 
    roc_curve, auc
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "selangor_training.csv"
MODEL_SAVE_PATH = BASE_DIR / "backend" / "models" / "incinerator_rf_model.pkl"
METRICS_DIR = BASE_DIR / "backend" / "static" / "metrics"

METRICS_DIR.mkdir(parents=True, exist_ok=True)

def train_model():
    print(" Starting Training Pipeline...")
    
    # 2. Load Data
    if not DATA_PATH.exists():
        print(f" Error: {DATA_PATH} not found")
        return

    df = pd.read_csv(DATA_PATH)
    feature_cols = ["population", "land_use", "dist_river_m", "dist_road_m"]
    X = df[feature_cols]
    y = df["suitable"]

    # 3. Academic Rigor: Cross-Validation
    # This proves the model's consistency across different data subsets
    rf_temp = RandomForestClassifier(n_estimators=100, random_state=42)
    cv_scores = cross_val_score(rf_temp, X, y, cv=5)
    print(f" 5-Fold Cross-Validation Mean Accuracy: {cv_scores.mean():.4f}")

    # 4. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 5. Final Model Training
    model = RandomForestClassifier(
        n_estimators=300, 
        max_depth=15,       # Prevent overfitting
        random_state=42,
        n_jobs=-1           # Use all CPU cores
    )
    model.fit(X_train, y_train)

    # 6. Evaluation & Visualizations (Crucial for Showcase)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # --- Confusion Matrix ---
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Not Suitable', 'Suitable'], 
                yticklabels=['Not Suitable', 'Suitable'])
    plt.title("Confusion Matrix: Site Suitability Prediction")
    plt.savefig(METRICS_DIR / "confusion_matrix.png")
    plt.close()

    # --- ROC Curve ---
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.title("Receiver Operating Characteristic (ROC)")
    plt.legend(loc="lower right")
    plt.savefig(METRICS_DIR / "roc_curve.png")
    plt.close()

    # --- Feature Importance ---
    plt.figure(figsize=(8, 6))
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances.sort_values().plot(kind='barh', color='skyblue')
    plt.title("Feature Importance Analysis")
    plt.savefig(METRICS_DIR / "feature_importance.png")
    plt.close()

    # 7. Save Model & Logs
    joblib.dump(model, MODEL_SAVE_PATH)
    
    # Save a text-based report for reference
    with open(METRICS_DIR / "classification_report.txt", "w") as f:
        f.write(classification_report(y_test, y_pred))

    print(f" Training Complete. Model saved to: {MODEL_SAVE_PATH}")
    print(f" Visualizations saved to: {METRICS_DIR}")

if __name__ == "__main__":
    train_model()