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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://www.etstur.com",
    "Referer": "https://www.etstur.com/",
}

def get_price():
    response = requests.post(API_URL, json=PAYLOAD, headers=HEADERS)

    if response.status_code != 200:
        return None, None, f"API hatası: {response.status_code}"

    data = response.json()

    # Bazı durumlarda "data" anahtarında olabilir
    items = data.get("data", data)

    if isinstance(items, list):
        for item in items:
            if item.get("roomName") == "Genel Görünüm":
                rp = item.get("roomPrice", {})
                discounted = rp.get("discountedPrice")
                normal = rp.get("amount")
                return discounted, normal, None

    return None, None, "Genel Görünüm için fiyat bulunamadı"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    discounted, normal, error = get_price()

    if error:
        msg = f"Voyage Sorgun (Genel Görünüm) Güncel Fiyat: {error}"
    else:
        discounted_str = f"{discounted:,.0f} TL" if discounted else "İndirimli fiyat bulunamadı"
        normal_str = f"{normal:,.0f} TL" if normal else "Fiyat bulunamadı"
        msg = (
            "Voyage Sorgun (Genel Görünüm) Güncel Fiyatlar:\n"
            f"İndirimli Fiyat: {discounted_str}\n"
            f"Normal Fiyat: {normal_str}"
        )

    print(msg)  # GitHub Actions log için
    send_telegram_message(msg)
