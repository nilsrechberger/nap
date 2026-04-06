import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def merge_processed_files(output_name: str = 'merged_data.csv') -> None:
    files = [os.path.join(PROCESSED_DIR, f) for f in os.listdir(PROCESSED_DIR) if f.endswith('.csv')]

    if not files:
        print("No CSV files found in processed folder.")
        return

    dfs = []
    for filepath in sorted(files):
        fname = os.path.basename(filepath)
        print(f"Reading {fname}...")
        try:
            df = pd.read_csv(filepath)
            dfs.append(df)
            print(f"  {len(df)} rows")
        except Exception as e:
            print(f"  Error reading {fname}: {e}")

    if not dfs:
        print("No data to merge.")
        return

    merged = pd.concat(dfs, ignore_index=True)
    merged = merged.drop_duplicates()

    out_path = os.path.join(PROCESSED_DIR, output_name)
    merged.to_csv(out_path, index=False)
    print(f"\nMerged {len(dfs)} files -> {len(merged)} rows saved to {output_name}")

if __name__ == '__main__':
    merge_processed_files()