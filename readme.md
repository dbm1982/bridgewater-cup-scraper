# Bridgewater Cup Scraper

Automated scraper for the Bridgewater Challenge Cup schedules on GotSport, with
per-division and filtered ICS calendars.

## How it works

1. `discover_event.py`
   - Loads the BYSA Challenge Cup landing page.
   - Finds the current GotSport event ID.
   - Finds all age/gender schedule URLs.

2. `discover_divisions.py`
   - Loads each age/gender page.
   - Extracts all division `group=` schedule URLs.
   - Saves them to `division_meta.json`.

3. `scrape_gotsport.py`
   - Scrapes each division `group=` URL.
   - Extracts all match rows into `gotsport_raw.csv`.

4. `normalize_gotsport.py`
   - Parses date/time, field, format, teams, and division.
   - Writes `gotsport_normalized.csv`.

5. `generate_ics.py`
   - Creates:
     - `bridgewater_cup_all.ics` (master calendar).
     - One `.ics` per division in `calendars/`.
     - One `_filtered.ics` per division including only matches where
       team names contain `HAYSA`, `Bulldogs`, `HOLA`, or `Bracket`.

## Subscribing

- Master calendar:

  `https://raw.githubusercontent.com/<user>/<repo>/main/bridgewater_cup_all.ics`

- Per-division calendar (example):

  `https://raw.githubusercontent.com/<user>/<repo>/main/calendars/BU8_-_Red.ics`

- Per-division filtered calendar (example):

  `https://raw.githubusercontent.com/<user>/<repo>/main/calendars/BU8_-_Red_filtered.ics`

Paste these URLs into Google/Apple/Outlook as "Subscribe from URL".

## Notes

- Playoff/Final brackets that use placeholder names containing "Bracket"
  will appear in the filtered ICS. If HAYSA/HOLA/Bulldogs do not advance,
  GotSport will update those names and the next run will drop those games
  from the filtered ICS automatically.
