import os
import pandas as pd

folder_path = 'scrap result'

csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
all_dfs = []

for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    df['source_file'] = file
    all_dfs.append(df)
combined_df = pd.concat(all_dfs, ignore_index=True)
combined_df.to_csv('all_glints.csv', index=False)
