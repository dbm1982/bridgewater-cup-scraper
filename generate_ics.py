import pandas as pd
from ics import Calendar, Event
import os
from collections import defaultdict
from datetime import datetime

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

    # Last refreshed timestamp
    last_updated = datetime.now().strftime("%b %d, %Y %I:%M %p")

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

            game_number = (
                row.get("game_id", "")
                or row.get("Game Number", "")
                or ""
            )

            event.description = (
                f"Field: {row['Location']}\n"
                f"Game #: {game_number}\n"
                f"Submit PINs: https://system.gotsport.com/org_event/events/52266/submit_pins/new\n\n"
                f"(last refreshed {last_updated})"
            )

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

        game_number = (
            row.get("game_id", "")
            or row.get("Game Number", "")
            or ""
        )

        event.description = (
            f"Field: {row['Location']}\n"
            f"Game #: {game_number}\n"
            f"Submit PINs: https://system.gotsport.com/org_event/events/52266/submit_pins/new\n\n"
            f"(last refreshed {last_updated})"
        )

        team_cals[home].events.add(event)
        team_cals[away].events.add(event)

    for team, cal in team_cals.items():

        # Determine correct division for this team
        first_event = next(iter(cal.events))
        # Extract division from the event description in df
        # We stored division only in the division ICS, so we re-derive it:
        # Look up any row matching this team
        sample_row = df[(df["Home Team"] == team) | (df["Away Team"] == team)].iloc[0]
        division = sample_row["Division"]
        agegroup = division.split()[0]  # GU12, BU8, etc.

        # Build safe filename
        safe_team = team.replace(" ", "_").replace("/", "_")
        safe = f"{safe_team}_{agegroup}"

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

        game_number = (
            row.get("game_id", "")
            or row.get("Game Number", "")
            or ""
        )

        event.description = (
            f"Field: {row['Location']}\n"
            f"Game #: {game_number}\n"
            f"Submit PINs: https://system.gotsport.com/org_event/events/52266/submit_pins/new\n\n"
            f"(last refreshed {last_updated})"
        )

        full.events.add(event)

    with open("bridgewater_cup_all.ics", "w") as f:
        f.writelines(full)

    print("Saved bridgewater_cup_all.ics")

if __name__ == "__main__":
    main()
