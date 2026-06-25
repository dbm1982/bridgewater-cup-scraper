from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os

HEADLESS = os.getenv("GITHUB_ACTIONS") == "true"

EVENT_URL = "https://system.gotsport.com/org_event/events/52266"

def discover_division_groups():
    divisions = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
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

        print(f"Scanning event page: {EVENT_URL}")
        page.goto(EVENT_URL, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        html = page.content()

        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)

    for a in links:
        href = a["href"]
        if "schedules?group=" in href:
            full_url = href if href.startswith("http") else "https://system.gotsport.com" + href
            name = a.get_text(strip=True)
            divisions.append({"name": name, "url": full_url})

    # Deduplicate
    seen = set()
    unique = []
    for d in divisions:
        if d["url"] not in seen:
            seen.add(d["url"])
            unique.append(d)

    with open("division_meta.json", "w") as f:
        json.dump({"divisions": unique}, f, indent=2)

    print("Discovered divisions:")
    for d in unique:
        print(f" - {d['name']}: {d['url']}")

if __name__ == "__main__":
    discover_division_groups()
