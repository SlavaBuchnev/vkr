import os
from pathlib import Path
import pandas as pd

def merge_csv_files(artifacts_dir='files/csv'):
    base = Path(artifacts_dir)
    if not base.exists():
        print(f"Directory '{artifacts_dir}' not found.")
        return

    # Все подпапки с префиксом results-
    result_dirs = [d for d in base.iterdir() if d.is_dir() and d.name.startswith('results-')]
    if not result_dirs:
        print(f"No 'results-*' folders found in '{artifacts_dir}'.")
        return

    dataframes = []
    for res_dir in result_dirs:
        csv_files = list(res_dir.glob('*.csv'))
        if not csv_files:
            print(f"No CSV files in {res_dir}")
            continue
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                dataframes.append(df)
                print(f"Loaded {csv_file} with {len(df)} rows")
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")

    if dataframes:
        combined = pd.concat(dataframes, ignore_index=True)
        combined.to_csv('ea_results.csv', index=False)
        print(f"Saved ea_results.csv with {len(combined)} rows")
    else:
        print("No valid data to merge")

if __name__ == "__main__":
    merge_csv_files()