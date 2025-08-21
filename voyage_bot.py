import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ")
CHAT_ID = os.getenv("CHAT_ID", "-1002950043362")

URL = "https://www.etstur.com/Voyage-Sorgun?check_in=06.09.2026&check_out=11.09.2026&adult_1=2&child_1=0"

def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    price_tag = soup.find("p", {"data-test-id": "price"})  # data-test-id ile bul
    if price_tag:
        return price_tag.get_text(strip=True)
    return "Fiyat bulunamadı"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    price = get_price()
    send_telegram_message(f"Voyage Sorgun Güncel Fiyat: {price}")
