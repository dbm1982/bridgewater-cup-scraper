import json
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

def load_divisions():
    with open("division_meta.json") as f:
        return json.load(f)["divisions"]

def fetch_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }
    print(f"Fetching: {url}")
    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    return r.text


# ------------------------------------------------------------
# PARSE POOL-PLAY TABLES
# ------------------------------------------------------------
def parse_schedule_table(table, division_name):
    rows = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)

    if len(rows) < 2:
        return None

    header = rows[0]
    data = rows[1:]

    df = pd.DataFrame(data, columns=header)

    # Ensure Division column exists
    if "Division" not in df.columns:
        df.insert(0, "Division", division_name)
    else:
        df["Division"] = division_name

    return df


# ------------------------------------------------------------
# ⭐ NEW: SCRAPE BRACKET GAMES FROM SAME PAGE
# ------------------------------------------------------------
def scrape_bracket_games_from_schedule_page(soup, division_name):
    games = []

    for game in soup.select(".bracket-game"):
        teams = game.select(".team-name")
        times = game.select(".game-time")
        fields = game.select(".game-field")

        if len(teams) == 2:
            home = teams[0].get_text(strip=True)
            away = teams[1].get_text(strip=True)
        else:
            continue

        time_str = times[0].get_text(strip=True) if times else ""
        field_str = fields[0].get_text(strip=True) if fields else ""

        games.append({
            "Division": division_name,
            "Match #": "",
            "Time": time_str,
            "Home Team": home,
            "Away Team": away,
            "Location": field_str,
            "Results": ""
        })

    return pd.DataFrame(games) if games else None


# ------------------------------------------------------------
# SCRAPE DIVISION (POOL + BRACKET)
# ------------------------------------------------------------
def scrape_division(div):
    all_tables = []
    base_url = div["url"]
    division_name = div["name"]

    print("DEBUG: Using base_url =", base_url)

    html = fetch_html(base_url)
    soup = BeautifulSoup(html, "html.parser")

    # 1. Scrape pool-play tables
    tables = soup.find_all("table")
    for table in tables:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

        if (
            "match #" in headers
            or ("time" in headers and "home" in headers and "away" in headers)
        ):
            df = parse_schedule_table(table, division_name)
            if df is not None:
                all_tables.append(df)

    # 2. Scrape bracket games from SAME page
    df_brackets = scrape_bracket_games_from_schedule_page(soup, division_name)
    if df_brackets is not None:
        print(f"Found {len(df_brackets)} bracket games for {division_name}")
        all_tables.append(df_brackets)
    else:
        print(f"No bracket games found for {division_name}")

    if not all_tables:
        print(f"No schedule tables found for {division_name}")
        return None

    return pd.concat(all_tables, ignore_index=True)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    divisions = load_divisions()
    all_schedules = []

    for div in divisions:
        print(f"Scraping division: {div['name']}")
        df = scrape_division(div)
        if df is not None:
            all_schedules.append(df)
        time.sleep(1)

    if not all_schedules:
        print("No schedules scraped.")
        return

    final_df = pd.concat(all_schedules, ignore_index=True)
    final_df.to_csv("gotsport_raw.csv", index=False)
    print("Saved gotsport_raw.csv")


if __name__ == "__main__":
    main()
