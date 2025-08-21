from playwright.sync_api import sync_playwright
import requests

BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.etstur.com/Voyage-Sorgun", timeout=60000)

    # Sayfa tamamen yüklenmesi için biraz bekletelim
    page.wait_for_timeout(5000)

    # Body içindeki tüm yazıları al
    all_text = page.inner_text("body")
    browser.close()

# Telegram karakter limitine göre parçalayarak gönder
chunk_size = 4000
for i in range(0, len(all_text), chunk_size):
    send_message(all_text[i:i+chunk_size])
