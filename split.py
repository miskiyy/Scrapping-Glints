import pandas as pd
import math

df = pd.read_csv("batch_01.csv")
batch_size = 5000
total_batches = math.ceil(len(df) / batch_size)

for i in range(total_batches):
    start = i * batch_size
    end = start + batch_size
    df_batch = df.iloc[start:end]
    df_batch.to_csv(f"batch_01_{i+1:02d}.csv", index=False)
    print(f"Saved batch_{i+1:02d}.csv")