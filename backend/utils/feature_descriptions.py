# app/feature_descriptions.py

LANDUSE_LABELS = {
    1: "Non-paddy agriculture",
    2: "Paddy fields",
    3: "Rural residential",
    4: "Urban residential",
    5: "Commercial/Institutional",
    6: "Industrial/Infrastructure",
    7: "Roads",
    8: "Urban",
    9: "Others"
}

POPULATION_LABELS = [
    (0, "Very low population"),
    (0.2, "Low population"),
    (0.4, "Moderate population"),
    (0.6, "High population"),
    (0.8, "Very high population")
]

def describe_population(norm_value):
    for threshold, label in POPULATION_LABELS:
        if norm_value >= threshold:
            selected = label
    return selected

def landuse_to_text(code):
    return LANDUSE_LABELS.get(code, "Unknown")
