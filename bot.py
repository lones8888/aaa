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

def get_prices():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.post(API_URL, json=PAYLOAD, headers=headers)

    if response.status_code == 200:
        data = response.json()

        discounted = None
        normal = None

        # Eğer liste dönüyorsa
        if isinstance(data, list):
            for item in data:
                if item.get("roomName") == "Genel Görünüm":
                    room_price = item.get("roomPrice", {})
                    discounted = room_price.get("discountedPrice")
                    normal = room_price.get("amount")
                    break
        # Eğer dict dönüyorsa
        elif isinstance(data, dict):
            if data.get("roomName") == "Genel Görünüm":
                room_price = data.get("roomPrice", {})
                discounted = room_price.get("discountedPrice")
                normal = room_price.get("amount")

        discounted_str = f"{discounted:,.0f} TL" if discounted else "İndirimli fiyat bulunamadı"
        normal_str = f"{normal:,.0f} TL" if normal else "Fiyat bulunamadı"

        return discounted_str, normal_str
    else:
        return "API hatası", "API hatası"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    discounted, normal = get_prices()
    msg = (
        "Voyage Sorgun Güncel Fiyatlar:\n"
        f"İndirimli Fiyat: {discounted}\n"
        f"Normal Fiyat: {normal}"
    )
    send_telegram_message(msg)
