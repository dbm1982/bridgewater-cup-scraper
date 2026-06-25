import pandas as pd
from ics import Calendar, Event
import os
from collections import defaultdict

def main():
    # Ensure folders exist
    os.makedirs("calendars", exist_ok=True)
    os.makedirs("calendars/teams", exist_ok=True)

    df = pd.read_csv("gotsport_normalized.csv")

    # Normalize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Required columns
    required = ["Division", "datetime", "Home Team", "Away Team", "Location"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # -----------------------------------------
    # DIVISION ICS GENERATION
    # -----------------------------------------
    divisions = df["Division"].unique()

    for div in divisions:
        cal = Calendar()
        subset = df[df["Division"] == div]

        for _, row in subset.iterrows():
            event = Event()
            event.name = f"{row['Home Team']} vs {row['Away Team']}"
            event.begin = row["datetime"]
            event.location = row["Location"]
            event.description = f"Division: {div}"
            cal.events.add(event)

        filename = f"calendars/{div.replace(' ', '_')}.ics"
        with open(filename, "w") as f:
            f.writelines(cal)

        print(f"Saved {filename}")

    # -----------------------------------------
    # PER-TEAM ICS GENERATION
    # -----------------------------------------
    team_cals = defaultdict(Calendar)

    for _, row in df.iterrows():
        home = row["Home Team"]
        away = row["Away Team"]

        event = Event()
        event.name = f"{home} vs {away}"
        event.begin = row["datetime"]
        event.location = row["Location"]
        event.description = f"Division: {row['Division']}"

        team_cals[home].events.add(event)
        team_cals[away].events.add(event)

    for team, cal in team_cals.items():
        safe = team.replace(" ", "_").replace("/", "_")
        filename = f"calendars/teams/{safe}.ics"
        with open(filename, "w") as f:
            f.writelines(cal)
        print(f"Saved {filename}")

    # -----------------------------------------
    # COMBINED ICS (ALL GAMES)
    # -----------------------------------------
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
