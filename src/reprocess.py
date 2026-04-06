# Build-in
import os
from datetime import date, datetime

# Data handling
import pandas as pd
from src.processor import as_table, remove_paid_content

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def reprocess_raw(filename: str = None) -> None:
    raw_dir = os.path.join(BASE_DIR, 'data', 'raw')
    processed_dir = os.path.join(BASE_DIR, 'data', 'processed')

    # Create processed directory if it doesn't exist
    os.makedirs(processed_dir, exist_ok=True)

    if filename:
        files = [os.path.join(raw_dir, filename)]
    else:
        # Check if directory exists to avoid FileNotFoundError
        if not os.path.exists(raw_dir):
            print(f"Error: Directory {raw_dir} does not exist.")
            return
        files = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith('.csv')]

    for filepath in files:
        fname = os.path.basename(filepath)
        out_name = fname.replace('raw_data_', 'processed_data_')
        out_path = os.path.join(processed_dir, out_name)

        if os.path.exists(out_path):
         print(f"  Skipping {fname}, already processed.")
         continue

        print(f"Reprocessing {fname}...")
        try:
            raw_df = pd.read_csv(filepath)

            # Placeholder for your cleaning logic
            # clean_df = remove_paid_content(raw_df)
            #clean_df = raw_df  # Remove this once remove_paid_content is defined
            clean_df = remove_paid_content(raw_df)

            clean_df.to_csv(out_path, index=False)
            print(f"  Saved {len(clean_df)} rows -> {out_name}")
        except Exception as e:
            print(f"  Error reprocessing {fname}: {e}")


reprocess_raw()