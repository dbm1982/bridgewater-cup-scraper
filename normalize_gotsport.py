import pandas as pd

def normalize_time(row):
    """
    Combine the date and time fields into a single datetime string.
    GotSport usually formats Time like:
    'Jun 28, 2026 9:10AM EDT'
    """
    t = row["Time"].replace("\n", " ").strip()
    return t

def main():
    df = pd.read_csv("gotsport_raw.csv")

    # Clean whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Normalize datetime
    df["datetime"] = df.apply(normalize_time, axis=1)

    # Clean team names
    df["Home Team"] = df["Home Team"].str.replace(r"\s+", " ", regex=True)
    df["Away Team"] = df["Away Team"].str.replace(r"\s+", " ", regex=True)

    # Clean location
    if "Location" in df.columns:
        df["Location"] = df["Location"].str.replace(r"\s+", " ", regex=True)

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
