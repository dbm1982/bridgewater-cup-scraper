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
    # TEAM ICS (DIVISION-SCOPED) — PATCHED
    # ----------------------------------------------------
    team_cals = defaultdict(lambda: defaultdict(Calendar))

    for _, row in df.iterrows():
        division = row["Division"]
        home = row["Home Team"].strip()
        away = row["Away Team"].strip()

        # Lowercase versions for matching
        home_lower = home.lower()
        away_lower = away.lower()

        # HAYSA/HOLA/Lady Bulldogs logic
        is_haysa_family = (
            "haysa" in home_lower or "haysa" in away_lower or
            "hola" in home_lower or "hola" in away_lower or
            "lady bulldogs" in home_lower or "lady bulldogs" in away_lower
        )

        # Bracket placeholder logic
        is_bracket_game = (
            "bracket" in home_lower or "bracket" in away_lower
        )

        # Create event
        event = Event()
        event.name = f"{home} vs {away}"
        event.begin = row["datetime"]
        event.location = row["Location"]

        game_number = row.get("Match #", "")

        event.description = (
            f"Field: {row['Location']}\n"
            f"Game #: {game_number}\n"
            f"Submit PINs: https://system.gotsport.com/org_event/events/52266/submit_pins/new\n\n"
            f"(last refreshed {last_updated})"
        )

        # Add event to BOTH teams within THIS division
        # (existing behavior)
        team_cals[division][home].events.add(event)
        team_cals[division][away].events.add(event)

        # NEW: Add bracket games to ALL HAYSA/HOLA/Lady Bulldogs teams
        if is_bracket_game or is_haysa_family:
            for team in team_cals[division].keys():
                team_cals[division][team].events.add(event)

    # Write team ICS files
    for division, teams in team_cals.items():
        agegroup = division.split()[0]  # e.g., BU8, GU10, etc.

        for team, cal in teams.items():
            if len(cal.events) == 0:
                continue

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
