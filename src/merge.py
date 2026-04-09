"""
merge.py — Merges processed daily CSV files one by one into a growing file.

Strategy:
  - Start from an existing merged file (if present) or from scratch
  - Load each new daily file, normalise its columns, append it to the merged result
  - Save after each file so progress is never lost

Handles three formats:
  Format A (new, with header, 22 cols)  — processed_data_YYYY-MM-DD.csv
  Format B (old, no header, 22 cols)    — col 0 = row_index, col 1 = article_id
  Format C (old, no header, 21 cols)    — col 0 = article_id

Run: python merge.py
Output: data/processed/processed_merged.csv
"""

import os
import re
import pandas as pd
from pathlib import Path

# ── PATHS ─────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUT_PATH      = PROCESSED_DIR / "merged data.csv"

# ── STANDARD COLUMNS (output schema) ─────────────────────────────────────────
STANDARD_COLS = [
    "article_id", "link", "title", "description", "keywords",
    "creator", "language", "country", "category", "datatype",
    "pubDate", "pubDateTZ", "fetched_at", "image_url", "video_url",
    "source_id", "source_name", "source_priority", "source_url",
    "source_icon", "duplicate", "source_date",
]

# ── COLUMN NAMES FOR OLD FORMATS ──────────────────────────────────────────────
COLS_WITH_IDX = [
    "row_index", "article_id", "link", "title", "description",
    "keywords", "creator", "language", "country", "category",
    "datatype", "pubDate", "pubDateTZ", "fetched_at", "image_url",
    "video_url", "source_id", "source_name", "source_priority",
    "source_url", "source_icon", "duplicate",
]

COLS_NO_IDX = [
    "article_id", "link", "title", "description", "keywords",
    "creator", "language", "country", "category", "datatype",
    "pubDate", "pubDateTZ", "fetched_at", "image_url", "video_url",
    "source_id", "source_name", "source_priority", "source_url",
    "source_icon", "duplicate",
]

ARTICLE_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")


def extract_date(filename: str) -> str:
    """Extract and normalise date string from filename → YYYY-MM-DD."""
    stem = filename.replace("processed_data_", "").replace(".csv", "")
    return stem.replace("_", "-")


def load_daily_file(path: Path) -> pd.DataFrame:
    """Load one daily processed file, normalise columns, return clean DataFrame."""
    # Peek at the file to detect format
    peek = pd.read_csv(path, nrows=1, dtype=str)

    if "article_id" in peek.columns:
        # Format A — proper header
        df = pd.read_csv(path, dtype=str)
        df = df.drop(columns=["Unnamed: 0"], errors="ignore")

    elif peek.shape[1] == 22:
        # Format B — no header, 22 cols, col 0 is row_index
        df = pd.read_csv(path, header=None, dtype=str)
        df.columns = COLS_WITH_IDX
        df = df.drop(columns=["row_index"], errors="ignore")

    else:
        # Format C — no header, 21 cols, col 0 is article_id
        df = pd.read_csv(path, header=None, dtype=str)
        df.columns = COLS_NO_IDX

    # Tag with source date
    df["source_date"] = extract_date(path.name)

    # Keep only rows with a valid 32-char hex article_id
    df = df[df["article_id"].str.match(ARTICLE_ID_PATTERN, na=False)].copy()

    # Align to standard columns — add missing ones as empty, drop extras
    for col in STANDARD_COLS:
        if col not in df.columns:
            df[col] = None
    df = df[STANDARD_COLS]

    return df


def merge_step_by_step() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Find all daily files (exclude the merged output itself)
    daily_files = sorted([
        f for f in PROCESSED_DIR.iterdir()
        if f.suffix == ".csv"
        and f.name.startswith("processed_data_")
        and f.name != OUT_PATH.name
    ])

    if not daily_files:
        print("No processed daily CSV files found in:", PROCESSED_DIR)
        return

    # Start from existing merged file if present, otherwise empty DataFrame
    if OUT_PATH.exists():
        merged = pd.read_csv(OUT_PATH, dtype=str)
        print(f"Starting from existing merged file: {len(merged):,} rows")
        already_seen = set(merged["source_date"].unique())
    else:
        merged = pd.DataFrame(columns=STANDARD_COLS)
        print("No existing merged file — starting from scratch")
        already_seen = set()

    print(f"\nFound {len(daily_files)} daily files:")

    for path in daily_files:
        date_str = extract_date(path.name)

        if date_str in already_seen:
            print(f"  {path.name:<45} already in merged — skipped")
            continue

        try:
            df = load_daily_file(path)
            rows_before = len(merged)
            merged = pd.concat([merged, df], ignore_index=True)

            # Save after each file so progress is never lost
            merged.to_csv(OUT_PATH, index=False)
            print(f"  {path.name:<45} +{len(df):>4} rows  →  total {len(merged):,}")

        except Exception as e:
            print(f"  {path.name} — ERROR: {e}")
            continue

    print(f"\n✅ Done → {OUT_PATH}")
    print(f"   Shape : {merged.shape[0]:,} rows × {merged.shape[1]} columns")
    print(f"\nRows per day:")
    print(merged["source_date"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    merge_step_by_step()