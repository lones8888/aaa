import requests

BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"

API_URL = "https://www.etstur.com/services/api/gallery-detail"

PAYLOAD = {
    "hotelId": "swr117krtpxn",
    "checkIn": "2026-09-06",
    "checkOut": "2026-09-11",
    "room": {
        "adultCount": 2,
        "childCount": 0,
        "childAges": [],
        "infantCount": 0
    }
}

def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.post(API_URL, json=PAYLOAD, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            price = data["discountedPrice"]
            return f"{price:,.0f} TL"
        except KeyError:
            return "JSON içinde discountedPrice bulunamadı"
    else:
        return f"API hatası: {response.status_code}"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    price = get_price()
    send_telegram_message(f"Voyage Sorgun Güncel Fiyat: {price}")

