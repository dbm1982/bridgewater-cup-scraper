import pandas as pd
from ics import Calendar, Event
import os
os.makedirs("calendars", exist_ok=True)


def main():
    df = pd.read_csv("gotsport_normalized.csv")

    # Normalize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Required columns
    required = ["Division", "datetime", "Home Team", "Away Team", "Location"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Create one ICS per division
    divisions = df["Division"].unique()

    for div in divisions:
        cal = Calendar()
        subset = df[df["Division"] == div]

        for _, row in subset.iterrows():
            event = Event()

            # Title: Home vs Away
            event.name = f"{row['Home Team']} vs {row['Away Team']}"

            # Start time
            event.begin = row["datetime"]

            # Location
            event.location = row["Location"]

            # Description
            event.description = f"Division: {div}"

            cal.events.add(event)

        # Save file
        filename = f"calendars/{div.replace(' ', '_')}.ics"
        with open(filename, "w") as f:
            f.writelines(cal)

        print(f"Saved {filename}")

    # Combined ICS
    full = Calendar()
    for _, row in df.iterrows():
        event = Event()
        event.name = f"{row['Home Team']} vs {row['Away Team']}"
        event.begin = row["datetime"]
        event.location = row["Location"]
        event.description = f"Division: {row['Division']}"
        full.events.add(event)

    with open("bridgewater_cup_all.ics", "w") as f:
        f.writelines(full)

    print("Saved bridgewater_cup_all.ics")

if __name__ == "__main__":
    main()
