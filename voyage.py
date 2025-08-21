import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"
URL = "https://www.etstur.com/Voyage-Sorgun"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message[:4000]}  # Telegram limit 4096
    requests.post(url, data=payload)

def main():
    # Sayfa kaynağını al
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    # HTML parse et
    soup = BeautifulSoup(resp.text, "html.parser")

    # Tüm yazıları topla
    text = soup.get_text(separator="\n", strip=True)

    # Telegram’a gönder
    send_telegram("Voyage Sorgun Sayfa İçeriği:\n\n" + text)

if __name__ == "__main__":
    main()
