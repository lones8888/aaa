from playwright.sync_api import sync_playwright
import requests

BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"

def send_photo(photo_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as f:
        requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": f})

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.etstur.com/Voyage-Sorgun")
    page.screenshot(path="voyage.png", full_page=True)
    browser.close()

send_photo("voyage.png")
