from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
import re

BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"

URL = "https://www.etstur.com/Voyage-Sorgun?check_in=2026-09-06&check_out=2026-09-11&adult_1=2&child_1=0"

def get_price():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    time.sleep(5)  # sayfanın yüklenmesini bekle

    html = driver.page_source
    driver.quit()

    match = re.search(r'"discountedPrice":\s*([\d\.]+)', html)
    if match:
        return f"{float(match.group(1)):,.0f} TL"
    else:
        return "İndirimli fiyat bulunamadı"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    price = get_price()
    send_telegram_message(f"Voyage Sorgun Güncel Fiyat (Selenium): {price}")
    print("✅ Telegram’a gönderildi:", price)

