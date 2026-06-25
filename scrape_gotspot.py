from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
import json

import os
HEADLESS = os.getenv("GITHUB_ACTIONS") == "true"


def scrape_division(div):
    name = div["name"]
    url = div["url"]
    print(f"Scraping division: {name} -> {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,   # ← FIXED HERE
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
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
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        page.goto(url, timeout=60000)
        page.wait_for_selector("table", timeout=60000)
        time.sleep(2)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        print("No tables found for division:", name)
        return None

    frames = []
    for table in tables:
        df = pd.read_html(str(table))[0]
        df["source_url"] = url
        df["division_name_raw"] = name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    return combined


def main():
    with open("division_meta.json") as f:
        meta = json.load(f)

    all_frames = []
    for div in meta["divisions"]:
        df = scrape_division(div)
        if df is not None:
            all_frames.append(df)

    if not all_frames:
        print("No data scraped.")
        return

    full = pd.concat(all_frames, ignore_index=True)
    full.to_csv("gotsport_raw.csv", index=False)
    print("Saved gotsport_raw.csv")


if __name__ == "__main__":
    main()
