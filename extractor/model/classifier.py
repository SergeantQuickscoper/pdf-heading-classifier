import pandas as pd
import glob
import os

data_dir = "trainingdata/"
all_files = glob.glob(os.path.join(data_dir, "*.csv"))

df_list = [pd.read_csv(file) for file in all_files]
df = pd.concat(df_list, ignore_index=True)

print(f"Loaded {len(df)} rows from {len(all_files)} files.")

print(df)
