import pandas as pd
from ics import Calendar, Event
import os
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

def parse_dt(dt_str):
    """Parse ISO datetime from CSV and attach EDT timezone."""
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("America/New_York"))
    return dt

def make_event(row, last_updated):
    """Create a fully formatted ICS event."""
    division = row["Division"]
    agegroup = division.split()[0]  # GU12, GU10, BU8, etc.

    event = Event()
    event.name = f"({agegroup}) {row['Home Team']} vs {row['Away Team']}"
    event.begin = parse_dt(row["datetime"])
    event.end = event.begin + timedelta(minutes=55)
    event.location = row["Location"]

    game_number = row.get("Match #", "")

    event.description = (
        f"Field: {row['Location']}\n"
        f"Game #: {game_number}\n"
        f"Submit PINs: https://system.gotsport.com/org_event/events/52266/submit_pins/new\n\n"
        f"(last refreshed {last_updated})"
    )

    return event

def main():
    os.makedirs("calendars", exist_ok=True)
    os.makedirs("calendars/teams", exist_ok=True)

    df = pd.read_csv("gotsport_normalized.csv")
    df.columns = [c.strip() for c in df.columns]

    last_updated = datetime.now(ZoneInfo("America/New_York")).strftime("%b %d, %Y %I:%M %p")

    # ----------------------------------------------------
    # DIVISION ICS
    # ----------------------------------------------------
    for div in df["Division"].unique():
        cal = Calendar()
        subset = df[df["Division"] == div].sort_values("datetime")

        for _, row in subset.iterrows():
            cal.events.add(make_event(row, last_updated))

        filename = f"calendars/{div.replace(' ', '_')}.ics"
        with open(filename, "w") as f:
            f.writelines(cal)

        print(f"Saved {filename}")

    # ----------------------------------------------------
    # TEAM ICS
    # ----------------------------------------------------
    team_cals = defaultdict(lambda: defaultdict(Calendar))

    for _, row in df.iterrows():
        division = row["Division"]
        home = row["Home Team"].strip()
        away = row["Away Team"].strip()

        event = make_event(row, last_updated)

        # Always add to both teams
        team_cals[division][home].events.add(event)
        team_cals[division][away].events.add(event)

        # ------------------------------------------------
        # ⭐ NEW: Add bracket games to ALL REAL TEAMS
        # ------------------------------------------------
        if "bracket" in home.lower() or "bracket" in away.lower():
            for t in team_cals[division].keys():
                # Skip bracket placeholder teams
                if not t.lower().startswith("bracket"):
                    team_cals[division][t].events.add(event)

    # Write team ICS files
    for division, teams in team_cals.items():
        agegroup = division.split()[0]

        for team, cal in teams.items():
            if len(cal.events) == 0:
                continue

            # Sort events
            cal.events = sorted(cal.events, key=lambda e: e.begin)

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
        full.events.add(make_event(row, last_updated))

    full.events = sorted(full.events, key=lambda e: e.begin)

    with open("bridgewater_cup_all.ics", "w") as f:
        f.writelines(full)

    print("Saved bridgewater_cup_all.ics")

if __name__ == "__main__":
    main()
