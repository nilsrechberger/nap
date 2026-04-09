<<<<<<< HEAD
# Build-in
import os
from datetime import date, datetime
=======
# Built-in
from datetime import datetime
from pathlib import Path
>>>>>>> 384a5db58a02df2315b6693e0078646ca6872e86

# Data handling
import pandas as pd

# Project packages
from src.crawler import fetch_data
from src.processor import as_table, remove_paid_content
<<<<<<< HEAD

TIMESTAMP = date.today()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
=======
>>>>>>> 384a5db58a02df2315b6693e0078646ca6872e86


RAW_PATH       = Path(f"data/raw/raw_data_{TIMESTAMP}.csv")
PROCESSED_PATH = Path(f"data/processed/processed_data_{TIMESTAMP}.csv")

countries = [
    "us", "gb", "ae", "af", "al", "dz", "as", "ad", "ao", "ai",
    "aq", "ag", "ar", "am", "aw", "au", "at", "az", "bs", "bh",
    "bd", "bb", "by", "be", "bz", "bj", "bm", "bt", "bo", "ba",
    "bw", "bv", "br", "io", "bn", "bg", "bf", "bi", "kh", "cm",
    "ca", "cv", "ky", "cf", "td", "cl", "cn", "cx", "co", "km",
    "cg", "cd", "ck", "cr", "ci", "hr", "je", "cu", "cy", "cw",
    "cz", "dk", "dj", "dm", "do", "tp", "ec", "eg", "sv", "gq",
    "er", "ee", "et", "fk", "fo", "fj", "fi", "fr", "gf", "pf",
    "tf", "ga", "gm", "ge", "de", "gh", "gi", "gr", "gl", "gd",
    "gp", "gu", "gt", "gn", "gw", "gy", "ht", "hm", "va", "hn",
    "tl", "hk", "hu", "is", "in", "id", "ir", "iq", "ie", "il",
    "it", "jm", "jp", "jo", "kz", "ke", "ki", "xk", "kp", "kr",
    "kw", "kg", "la", "lv", "lb", "ls", "lr", "ly", "li", "lt",
    "lu", "mo", "mk", "mg", "mw", "my", "mv", "ml", "mt", "mh",
    "mq", "mr", "mu", "yt", "mx", "fm", "md", "mc", "mn", "ms",
    "ma", "mz", "mm", "me", "na", "nr", "np", "nl", "an", "nc",
    "nz", "ni", "ne", "ng", "nu", "nf", "mp", "no", "om", "pk",
    "pw", "ps", "pa", "pg", "py", "pe", "ph", "pn", "pl", "pt",
    "pr", "qa", "re", "ro", "ru", "rw", "sh", "kn", "lc", "pm",
    "vc", "ws", "sm", "st", "sa", "sn", "sc", "sl", "sg", "sk",
    "si", "sb", "so", "za", "gs", "es", "lk", "sd", "sr", "sj",
    "sz", "se", "ch", "sy", "tw", "tj", "tz", "th", "tg", "tk",
    "to", "tt", "tn", "tr", "tm", "tc", "tv", "ug", "ua", "uy",
    "uz", "vu", "ve", "vi", "vg", "wf", "eh", "ye", "yu", "zm",
    "zw", "rs", "sx", "wo",
]


def main() -> None:
<<<<<<< HEAD
    tables = []

    country_codes = [
        "us", "gb", "ae", "af", "al", "dz", "as", "ad", "ao", "ai",
        "aq", "ag", "ar", "am", "aw", "au", "at", "az", "bs", "bh",
        "bd", "bb", "by", "be", "bz", "bj", "bm", "bt", "bo", "ba",
        "bw", "bv", "br", "io", "bn", "bg", "bf", "bi", "kh", "cm",
        "ca", "cv", "ky", "cf", "td", "cl", "cn", "cx", "co", "km",
        "cg", "cd", "ck", "cr", "ci", "hr", "je", "cu", "cy", "cw",
        "cz", "dk", "dj", "dm", "do", "tp", "ec", "eg", "sv", "gq",
        "er", "ee", "et", "fk", "fo", "fj", "fi", "fr", "gf", "pf",
        "tf", "ga", "gm", "ge", "de", "gh", "gi", "gr", "gl", "gd",
        "gp", "gu", "gt", "gn", "gw", "gy", "ht", "hm", "va", "hn",
        "tl", "hk", "hu", "is", "in", "id", "ir", "iq", "ie", "il",
        "it", "jm", "jp", "jo", "kz", "ke", "ki", "xk", "kp", "kr",
        "kw", "kg", "la", "lv", "lb", "ls", "lr", "ly", "li", "lt",
        "lu", "mo", "mk", "mg", "mw", "my", "mv", "ml", "mt", "mh",
        "mq", "mr", "mu", "yt", "mx", "fm", "md", "mc", "mn", "ms",
        "ma", "mz", "mm", "me", "na", "nr", "np", "nl", "an", "nc",
        "nz", "ni", "ne", "ng", "nu", "nf", "mp", "no", "om", "pk",
        "pw", "ps", "pa", "pg", "py", "pe", "ph", "pn", "pl", "pt",
        "pr", "qa", "re", "ro", "ru", "rw", "sh", "kn", "lc", "pm",
        "vc", "ws", "sm", "st", "sa", "sn", "sc", "sl", "sg", "sk",
        "si", "sb", "so", "za", "gs", "es", "lk", "sd", "sr", "sj",
        "sz", "se", "ch", "sy", "tw", "tj", "tz", "th", "tg", "tk",
        "to", "tt", "tn", "tr", "tm", "tc", "tv", "ug", "ua", "uy",
        "uz", "vu", "ve", "vi", "vg", "wf", "eh", "ye", "yu", "zm",
        "zw", "rs", "sx", "wo"
    ]

    for country in country_codes:
        print(f"Fetching {country}...")

        try:
            raw_data = fetch_data(country)

            if not raw_data or 'results' not in raw_data:
                print(f"  No data for {country}, skipping...")
                continue

            if not isinstance(raw_data['results'], list) or len(raw_data['results']) == 0:
                print(f"  Empty or invalid results for {country}, skipping...")
                continue

            tables.append(as_table(raw_data))
            print(f"  Got {len(raw_data['results'])} articles")

        except Exception as e:
            print(f"  Error for {country}: {e}")
            continue

    results = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()

    results.to_csv(os.path.join(BASE_DIR, f'data/raw/raw_data_{TIMESTAMP}.csv'), index=False)

    clean_results = remove_paid_content(results)
    print(f"Processed {len(clean_results)} rows.")
    clean_results.to_csv(os.path.join(BASE_DIR, f'data/processed/processed_data_{TIMESTAMP}.csv'), index=False)




if __name__ == '__main__':
    main()
    #reprocess_raw()                           # reprocess all unmatched files
    # reprocess_raw('raw_data_2026-04-01.csv')  # reprocess a specific file
=======
    # Create output directories automatically if they don't exist
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

    results = pd.DataFrame()

    # ── DEBUG: inspect a single country first ─────────────────────────────────
    # Uncomment the 3 lines below, run once, check what the API returns,
    # then comment them out again before the full run.
    #
    # test = fetch_data("us")
    # print("API response keys:", test.keys() if test else "None")
    # print("API response sample:", str(test)[:500])
    # return
    # ─────────────────────────────────────────────────────────────────────────

    for country in countries:
        print(f"Fetching {country}...")

        try:
            raw_data = fetch_data(country)

            # Debug: print the raw response for the first country to inspect structure
            if results.empty:
                print(f"  DEBUG first response keys: {list(raw_data.keys()) if raw_data else 'None'}")
                print(f"  DEBUG first response sample: {str(raw_data)[:300]}")

            if not raw_data or "results" not in raw_data:
                print(f"  No data for {country}, skipping...")
                continue

            # Stop immediately if API limit is hit
            if isinstance(raw_data["results"], dict):
                code = raw_data["results"].get("code", "")
                if code in ("RateLimitExceeded", "ApiLimitExceeded"):
                    print(f"\n  API limit exceeded — stopping early. Try again tomorrow.")
                    break

            if not isinstance(raw_data["results"], list) or len(raw_data["results"]) == 0:
                print(f"  Empty or invalid results for {country}, skipping...")
                continue

            table = as_table(raw_data)
            results = pd.concat([results, table], ignore_index=True)
            print(f"  Got {len(raw_data['results'])} articles")

        except Exception as e:
            print(f"  Error for {country}: {e}")
            continue

    if results.empty:
        print("No data collected — nothing saved.")
        return

    results.to_csv(RAW_PATH, index=False)
    print(f"Raw data saved       → {RAW_PATH}  ({len(results):,} rows)")

    clean_results = remove_paid_content(results.astype(str))
    clean_results.to_csv(PROCESSED_PATH, index=False)
    print(f"Processed data saved → {PROCESSED_PATH}  ({len(clean_results):,} rows, {len(clean_results.columns)} columns)")


if __name__ == "__main__":
    main()
>>>>>>> 384a5db58a02df2315b6693e0078646ca6872e86
