from ics import Calendar, Event
import pandas as pd
from datetime import timedelta
import os

FILTER_KEYWORDS = ["haysa", "bulldogs", "hola", "bracket"]

def safe(s):
    return (
        str(s)
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace("__", "_")
    )

def match_filter(event_name):
    name = event_name.lower()
    return any(keyword in name for keyword in FILTER_KEYWORDS)

df = pd.read_csv("gotsport_normalized.csv")

master_cal = Calendar()
division_cals = {}

for _, row in df.iterrows():
    div = row["division"]
    if div not in division_cals:
        division_cals[div] = Calendar()

    event = Event()
    event.name = f"{row['home_team']} vs {row['away_team']} ({row['division']})"
    event.begin = row["datetime"]
    event.duration = timedelta(hours=1)  # adjust if needed
    event.location = row["Location"]
    event.uid = f"match-{row['match_id']}@bridgewatercup"

    master_cal.events.add(event)
    division_cals[div].events.add(event)

with open("bridgewater_cup_all.ics", "w") as f:
    f.writelines(master_cal)

os.makedirs("calendars", exist_ok=True)

for div, cal in division_cals.items():
    safe_div = safe(div)

    # Full division ICS
    full_path = f"calendars/{safe_div}.ics"
    with open(full_path, "w") as f:
        f.writelines(cal)

    # Filtered ICS (HAYSA / Bulldogs / HOLA / Bracket)
    filtered = Calendar()
    for event in cal.events:
        if match_filter(event.name):
            filtered.events.add(event)

    if len(filtered.events) > 0:
        filtered_path = f"calendars/{safe_div}_filtered.ics"
        with open(filtered_path, "w") as f:
            f.writelines(filtered)

print("ICS generation complete.")
