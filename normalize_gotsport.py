import pandas as pd
import unicodedata
import re
from datetime import datetime

def normalize_unicode_spaces(s):
    if not isinstance(s, str):
        return s

    # Normalize unicode (converts many weird spaces to standard forms)
    s = unicodedata.normalize("NFKC", s)

    # Remove zero-width characters (ZWNJ, ZWJ, BOM)
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)

    # Replace ALL unicode whitespace with normal spaces
    cleaned = "".join(
        " " if unicodedata.category(c).startswith("Z") else c
        for c in s
    )

    return cleaned

def normalize_time(row):
    raw = row["Time"].replace("\n", " ").strip()
    dt = datetime.strptime(raw, "%b %d, %Y %I:%M%p EDT")
    return dt.strftime("%Y-%m-%dT%H:%M:%S-04:00")

def main():
    df = pd.read_csv("gotsport_raw.csv")

    # ---------------------------------------------------------
    # Normalize ALL unicode whitespace column-by-column
    # ---------------------------------------------------------
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].map(normalize_unicode_spaces)

    # ---------------------------------------------------------
    # Collapse normal whitespace
    # ---------------------------------------------------------
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
            )

    # ---------------------------------------------------------
    # Normalize datetime
    # ---------------------------------------------------------
    df["datetime"] = df.apply(normalize_time, axis=1)

    # ---------------------------------------------------------
    # Final column order
    # ---------------------------------------------------------
    keep_cols = [
        "Division",
        "Match #",
        "datetime",
        "Home Team",
        "Results",
        "Away Team",
        "Location",
    ]

    keep_cols = [c for c in keep_cols if c in df.columns]
    final = df[keep_cols]

    final.to_csv("gotsport_normalized.csv", index=False)
    print("Saved gotsport_normalized.csv")

if __name__ == "__main__":
    main()
