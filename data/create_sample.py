import pandas as pd

df = pd.read_csv("data/raw_prs.csv")
sample = df.sample(n=300, random_state=42)
sample.to_csv("data/labelling_sample.csv", index=False)
print("Created labelling_sample.csv with 300 rows")