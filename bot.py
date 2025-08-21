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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://www.etstur.com",
    "Referer": "https://www.etstur.com/",
    "Cookie": "meiro_user_id_js=4d7991a8-23a6-4a2b-a868-45b51f548c36; "
              "hotelSearchCheckIn=2026-09-06; "
              "hotelSearchCheckOut=2026-09-11; "
              "guest=%7B%22adultCount%22%3A2%2C%22childCount%22%3A0%2C%22childAges%22%3A%5B%5D%2C%22infantCount%22%3A0%7D; "
              "meiro_session_id_js=MTc1NTc5NzMyNzU3NCY0ZDc5OTFhOC0yM2E2LTRhMmItYTg2OC00NWI1MWY1NDhjMzY=; "
              "meiro_session_id_used_ts_js=1755799014116; "
              "SESSION=MGNmMzY2OTgtZTQ0ZC00ZmY0LWE3YTEtNDNiYmU2MzViODM0"
}

def get_price():
    response = requests.post(API_URL, json=PAYLOAD, headers=HEADERS)

    if response.status_code != 200:
        return None, None, f"API hatası: {response.status_code}"

    data = response.json()
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

    print(msg)
    send_telegram_message(msg)
