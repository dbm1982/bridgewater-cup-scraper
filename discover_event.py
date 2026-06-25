from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

def discover_event(base_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(base_url, timeout=60000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Extract event ID from any schedule link
    links = soup.find_all("a", href=True)
    event_ids = set()

    for a in links:
        m = re.search(r"/events/(\d+)/", a["href"])
        if m:
            event_ids.add(m.group(1))

    if not event_ids:
        raise Exception("No event ID found")

    event_id = list(event_ids)[0]

    # Extract all age/gender schedule links
    schedule_urls = set()
    for a in links:
        if "schedules?age=" in a["href"]:
            schedule_urls.add("https://system.gotsport.com" + a["href"])

    return event_id, list(schedule_urls)

if __name__ == "__main__":
    event_id, urls = discover_event("https://bridgewateryouthsoccer.org/challenge-cup")
    print("EVENT:", event_id)
    print("URLS:", urls)
