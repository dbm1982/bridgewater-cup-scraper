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
    df.columns = [c.strip() for c in df.columns]

    required = ["Division", "Match #", "datetime", "Home Team", "Away Team", "Location"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    last_updated = datetime.now().strftime("%b %d, %Y %I:%M %p")

    # ----------------------------------------------------
    # DIVISION ICS
    # ----------------------------------------------------
    for div in df["Division"].unique():
        cal = Calendar()
        subset = df[df["Division"] == div]

        for _, row in subset.iterrows():
            event = Event()
            event.name = f"{row['Home Team']} vs {row['Away Team']}"
            event.begin = row["datetime"]
            event.location = row["Location"]

            game_number = row.get("Match #", "")

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

    # ----------------------------------------------------
    # TEAM ICS
    # ----------------------------------------------------
    team_cals = defaultdict(Calendar)

    for _, row in df.iterrows():
        home = row["Home Team"].strip()
        away = row["Away Team"].strip()

        # Normalize bracket teams
        if "Bracket" in home:
            home = home.strip()
        if "Bracket" in away:
            away = away.strip()

        event = Event()
        event.name = f"{row['Home Team']} vs {row['Away Team']}"
        event.begin = row["datetime"]
        event.location = row["Location"]

        game_number = row.get("Match #", "")

        event.description = (
            f"Field: {row['Location']}\n"
            f"Game #: {game_number}\n"
            f"Submit PINs: https://system.gotsport.com/org_event/events/52266/submit_pins/new\n\n"
            f"(last refreshed {last_updated})"
        )

        team_cals[home].events.add(event)
        team_cals[away].events.add(event)

    for team, cal in team_cals.items():

        if len(cal.events) == 0:
            continue

        sample = df[(df["Home Team"] == team) | (df["Away Team"] == team)]
        if sample.empty:
            continue

        division = sample.iloc[0]["Division"]
        agegroup = division.split()[0]

        safe_team = team.replace(" ", "_").replace("/", "_")
        filename = f"calendars/teams/{safe_team}_{agegroup}.ics"

        with open(filename, "w") as f:
            f.writelines(cal)

        print(f"Saved {filename}")

    # ----------------------------------------------------
    # COMBINED ICS
    # ----------------------------------------------------
    full = Calendar()

    for _, row in df.iterrows():
        event = Event()
        event.name = f"{row['Home Team']} vs {row['Away Team']}"
        event.begin = row["datetime"]
        event.location = row["Location"]

        game_number = row.get("Match #", "")

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
