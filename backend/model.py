import joblib

def load_model(path="models/incinerator_rf_model.pkl"):
    model = joblib.load(path)
    return model