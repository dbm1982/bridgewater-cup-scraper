import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

HEADLESS = True

def load_divisions():
    with open("division_meta.json") as f:
        return json.load(f)["divisions"]

def get_page_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1400, "height": 900},
            java_script_enabled=True,
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

        print(f"Loading: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        html = page.content()

        browser.close()
        return html

def parse_standings_table(table):
    rows = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)

    if len(rows) < 2:
        return None

    header = rows[0]
    data = rows[1:]
    return pd.DataFrame(data, columns=header)

def parse_schedule_table(table):
    rows = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)

    if len(rows) < 2:
        return None

    header = rows[0]
    data = rows[1:]
    return pd.DataFrame(data, columns=header)

def scrape_division(div):
    url = div["url"]
    html = get_page_html(url)
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    if not tables:
        print(f"No tables found for {div['name']}")
        return None

    standings = None
    schedule = None

    for table in tables:
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

        if "team" in headers and "pts" in headers:
            standings = parse_standings_table(table)

        if "time" in headers and "home" in headers and "away" in headers:
            schedule = parse_schedule_table(table)

    if standings is None and schedule is None:
        print(f"No usable tables for {div['name']}")
        return None

    # Tag division name
    if standings is not None:
        standings.insert(0, "Division", div["name"])

    if schedule is not None:
        schedule.insert(0, "Division", div["name"])

    return standings, schedule

def main():
    divisions = load_divisions()
    all_rows = []

    for div in divisions:
        print(f"Scraping division: {div['name']} -> {div['url']}")
        result = scrape_division(div)

        if result is None:
            continue

        standings, schedule = result

        if standings is not None:
            all_rows.append(standings)

        if schedule is not None:
            all_rows.append(schedule)

        time.sleep(1)

    if not all_rows:
        print("No data scraped.")
        return

    final_df = pd.concat(all_rows, ignore_index=True)
    final_df.to_csv("gotsport_raw.csv", index=False)
    print("Saved gotsport_raw.csv")

if __name__ == "__main__":
    main()
