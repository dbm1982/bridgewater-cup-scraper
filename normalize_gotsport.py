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

    # ---------------------------------------------------------
    # FIX: pandas 3.0 removed applymap()
    # Normalize unicode whitespace column-by-column
    # ---------------------------------------------------------
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].map(
                lambda x: x.replace("\u00A0", " ") if isinstance(x, str) else x
            )

    # Clean whitespace for string columns only
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
            )

    # Normalize datetime
    df["datetime"] = df.apply(normalize_time, axis=1)

    # Clean team names (Bracket-safe)
    if "Home Team" in df.columns:
        df["Home Team"] = df["Home Team"].astype(str).str.strip()

    if "Away Team" in df.columns:
        df["Away Team"] = df["Away Team"].astype(str).str.strip()

    # Clean location
    if "Location" in df.columns:
        df["Location"] = df["Location"].astype(str).str.strip()

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

    keep_cols = [c for c in keep_cols if c in df.columns]

    final = df[keep_cols]

    final.to_csv("gotsport_normalized.csv", index=False)
    print("Saved gotsport_normalized.csv")

if __name__ == "__main__":
    main()
