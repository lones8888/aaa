import requests
import json

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

    if response.status_code != 200:
        return None, None, f"API hatası: {response.status_code}"

    data = response.json()

    # DEBUG JSON dosyaya kaydet
    with open("debug.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ debug.json dosyasına yazıldı, lütfen açıp ilk 30 satırını paylaş")

    discounted = None
    normal = None

    items = data.get("data", data)

    if isinstance(items, list):
        for item in items:
            if item.get("roomName") == "Genel Görünüm":
                room_price = item.get("roomPrice", {})
                discounted = room_price.get("discountedPrice")
                normal = room_price.get("amount")
                break
    elif isinstance(items, dict):
        if items.get("roomName") == "Genel Görünüm":
            room_price = items.get("roomPrice", {})
            discounted = room_price.get("discountedPrice")
            normal = room_price.get("amount")

    return discounted, normal, None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    r = requests.post(url, data=payload)
    print("Telegram status:", r.status_code, r.text)

if __name__ == "__main__":
    discounted, normal, err = get_prices()

    if err:
        msg = f"Voyage Sorgun Güncel Fiyatlar:\nHata: {err}"
    else:
        discounted_str = f"{discounted:,.0f} TL" if discounted else "İndirimli fiyat bulunamadı"
        normal_str = f"{normal:,.0f} TL" if normal else "Fiyat bulunamadı"
        msg = (
            "Voyage Sorgun Güncel Fiyatlar:\n"
            f"İndirimli Fiyat: {discounted_str}\n"
            f"Normal Fiyat: {normal_str}"
        )

    send_telegram_message(msg)
