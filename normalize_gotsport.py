import pandas as pd
from datetime import datetime

def normalize_time(row):
    """
    Convert 'Jun 27, 2026 8:00AM EDT' → '2026-06-27T08:00:00-04:00'
    """
    raw = row["Time"].replace("\n", " ").strip()

    # Parse the GotSport format
    dt = datetime.strptime(raw, "%b %d, %Y %I:%M%p EDT")

    # EDT = UTC-4
    return dt.strftime("%Y-%m-%dT%H:%M:%S-04:00")

def main():
    df = pd.read_csv("gotsport_raw.csv")

    # Clean whitespace for string columns only (pandas 3.0-safe)
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

    # Normalize datetime
    df["datetime"] = df.apply(normalize_time, axis=1)

    # ---------------------------------------------------------
    # TEAM NAME CLEANING (Bracket-safe)
    # ---------------------------------------------------------
    # We DO want to collapse weird whitespace, but we DO NOT want
    # to strip out the word "Bracket" or merge it incorrectly.
    #
    # Example:
    #   "Bracket A" → keep
    #   "Bracket   A" → collapse to "Bracket A"
    #   "BracketA" → keep as-is
    #
    # This preserves all Bracket teams.
    # ---------------------------------------------------------

    if "Home Team" in df.columns:
        df["Home Team"] = (
            df["Home Team"]
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    if "Away Team" in df.columns:
        df["Away Team"] = (
            df["Away Team"]
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    # Clean location
    if "Location" in df.columns:
        df["Location"] = (
            df["Location"]
            .astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    # Final column order
    keep_cols = [
        "Division",
        "Match #",
        "datetime",
        "Home Team",
        "Results",
        "Away Team",
        "Location",
    ]

    # Only keep columns that actually exist
    keep_cols = [c for c in keep_cols if c in df.columns]

    final = df[keep_cols]

    final.to_csv("gotsport_normalized.csv", index=False)
    print("Saved gotsport_normalized.csv")

if __name__ == "__main__":
    main()
