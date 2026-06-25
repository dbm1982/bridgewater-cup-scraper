import pandas as pd
from datetime import datetime
import re

df = pd.read_csv("gotsport_raw.csv")

def parse_datetime(s):
    s = str(s).replace("  ", " ").replace(" EDT", "")
    return datetime.strptime(s, "%b %d, %Y %I:%M%p")

df["datetime"] = df["Time"].apply(parse_datetime)
df["date"] = df["datetime"].dt.date
df["time"] = df["datetime"].dt.time

def split_field_format(location):
    parts = str(location).split(" - ")
    if len(parts) >= 3:
        return parts[1], parts[2]
    return None, None

df["field"], df["format"] = zip(*df["Location"].apply(split_field_format))

def clean_team(name):
    name = re.sub(r"\s+", " ", str(name).strip())
    return name

df["home_team"] = df["Home Team"].apply(clean_team)
df["away_team"] = df["Away Team"].apply(clean_team)

# Use GotSport division column if present, else the raw name we captured
if "Division" in df.columns:
    df["division"] = df["Division"].astype(str).str.strip()
else:
    df["division"] = df["division_name_raw"].astype(str).str.strip()

df["match_id"] = df["Match #"]

final = df[
    [
        "match_id",
        "division",
        "date",
        "time",
        "datetime",
        "home_team",
        "away_team",
        "field",
        "format",
        "Location",
        "source_url",
    ]
]

final.to_csv("gotsport_normalized.csv", index=False)
print("Saved gotsport_normalized.csv")
