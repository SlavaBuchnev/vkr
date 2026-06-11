import glob
import pandas as pd

def merge_csv_files():
    csv_files = glob.glob('results_*.csv')
    if not csv_files:
        print("No results_*.csv files found.")
        return

    dataframes = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            dataframes.append(df)
            print(f"Loaded {f} with {len(df)} rows")
        except Exception as e:
            print(f"Error reading {f}: {e}")

    if dataframes:
        combined = pd.concat(dataframes, ignore_index=True)
        combined.to_csv('combined_results.csv', index=False)
        print(f"Saved combined_results.csv with {len(combined)} rows")
    else:
        print("No valid data to merge")

if __name__ == "__main__":
    merge_csv_files()