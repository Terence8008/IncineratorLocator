from data_processing import compute_mcda
import pandas as pd

df = pd.read_csv("data/selangor_sample_points_features.csv")

df = compute_mcda(df)

df.to_csv("data/selangor_sample_points_full.csv", index=False)
print("Saved MCDA-labeled dataset")