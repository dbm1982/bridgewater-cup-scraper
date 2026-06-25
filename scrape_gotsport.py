import json
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

TOURNAMENT_DATES = [
    "2026-06-26",
    "2026-06-27",
    "2026-06-28",
]

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
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

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

    if "Division" not in df.columns:
        df.insert(0, "Division", division_name)
    else:
        df["Division"] = division_name

    return df

def scrape_division(div):
    all_days = []
    base_url = div["url"]

    # ----------------------------------------------------
    # 1. SCRAPE FULL BRACKET/DIVISION PAGE (NO DATE FILTER)
    # ----------------------------------------------------
    html = fetch_html(base_url)
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    for table in tables:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if (
            "match #" in headers
            or ("time" in headers and "home" in headers and "away" in headers)
        ):
            df = parse_schedule_table(table, div["name"])
            if df is not None:
                all_days.append(df)
            break

    # ----------------------------------------------------
    # 2. SCRAPE EACH DATE PAGE (POOL GAMES)
    # ----------------------------------------------------
    for date in TOURNAMENT_DATES:
        url = f"{base_url}&date={date}"
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        tables = soup.find_all("table")
        for table in tables:
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if (
                "match #" in headers
                or ("time" in headers and "home" in headers and "away" in headers)
            ):
                df = parse_schedule_table(table, div["name"])
                if df is not None:
                    all_days.append(df)
                break

        time.sleep(0.5)

    if not all_days:
        print(f"No schedules found for {div['name']}")
        return None

    return pd.concat(all_days, ignore_index=True)

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
