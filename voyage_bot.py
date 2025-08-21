import requests
import re
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKENINIZI_GIRIN")
CHAT_ID = os.getenv("CHAT_ID", "CHAT_IDINIZI_GIRIN")

URL = "https://www.etstur.com/Voyage-Sorgun?check_in=06.09.2026&check_out=11.09.2026&adult_1=2&child_1=0"

def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    match = re.search(r"(\d{1,3}(?:\.\d{3})*)\s*TL", response.text)
    if match:
        return match.group(0)
    return "Fiyat bulunamadı"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    price = get_price()
    send_telegram_message(f"Voyage Sorgun Güncel Fiyat: {price}")
