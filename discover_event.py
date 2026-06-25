from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import json
from config import TOURNAMENT_LANDING_URL

import os
HEADLESS = os.getenv("GITHUB_ACTIONS") == "true"

def discover_event_and_age_gender_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = browser.new_page()
        page.goto(TOURNAMENT_LANDING_URL, timeout=60000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)

    event_ids = set()
    age_gender_urls = set()

    for a in links:
        href = a["href"]
        m = re.search(r"/org_event/events/(\d+)/", href)
        if m:
            event_ids.add(m.group(1))
        if "schedules?age=" in href:
            if href.startswith("http"):
                age_gender_urls.add(href)
            else:
                age_gender_urls.add("https://system.gotsport.com" + href)

    if not event_ids:
        raise Exception("No event ID found on landing page")

    event_id = list(event_ids)[0]

    meta = {
        "event_id": event_id,
        "age_gender_urls": sorted(age_gender_urls),
    }

    with open("event_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("Discovered event_id:", event_id)
    print("Discovered age/gender URLs:")
    for u in meta["age_gender_urls"]:
        print(" -", u)

if __name__ == "__main__":
    discover_event_and_age_gender_pages()
