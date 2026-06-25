from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re

def discover_division_groups():
    with open("event_meta.json") as f:
        meta = json.load(f)

    age_gender_urls = meta["age_gender_urls"]
    divisions = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
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

        for url in age_gender_urls:
            print(f"Scanning age/gender page: {url}")
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=60000)
            html = page.content()

            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=True)

            for a in links:
                href = a["href"]
                if "schedules?group=" in href:
                    full_url = href if href.startswith("http") else "https://system.gotsport.com" + href
                    name = a.get_text(strip=True)
                    divisions.append({"name": name, "url": full_url})

        browser.close()

    # Deduplicate by URL
    seen = set()
    unique_divisions = []
    for d in divisions:
        if d["url"] not in seen:
            seen.add(d["url"])
            unique_divisions.append(d)

    with open("division_meta.json", "w") as f:
        json.dump({"divisions": unique_divisions}, f, indent=2)

    print("Discovered divisions:")
    for d in unique_divisions:
        print(f" - {d['name']}: {d['url']}")

if __name__ == "__main__":
    discover_division_groups()
