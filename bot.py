import requests

BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"

URL = "https://www.etstur.com/Voyage-Sorgun?check_in=2026-09-06&check_out=2026-09-11&adult_1=2&child_1=0"

# Tarayıcıdan aldığın cookie’yi buraya yapıştır
COOKIES = {
    "meiro_user_id_js": "4d7991a8-23a6-4a2b-a868-45b51f548c36",
    "hotelSearchCheckIn": "2026-09-06",
    "hotelSearchCheckOut": "2026-09-11",
    "guest": '{"adultCount":2,"childCount":0,"childAges":[],"infantCount":0}',
    "meiro_session_id_js": "MTc1NTc5NzMyNzU3NCY0ZDc5OTFhOC0yM2E2LTRhMmItYTg2OC00NWI1MWY1NDhjMzY=",
    "meiro_session_id_used_ts_js": "1755799014116",
    "SESSION": "MGNmMzY2OTgtZTQ0ZC00ZmY0LWE3YTEtNDNiYmU2MzViODM0"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"
}

def get_price():
    response = requests.get(URL, headers=HEADERS, cookies=COOKIES)
    if response.status_code != 200:
        return f"API hatası: {response.status_code}"

    html = response.text

    # JSON'dan fiyatları çekmek için basit bir arama
    import re
    match = re.search(r'"discountedPrice":\s*([\d\.]+)', html)
    if match:
        return f"{float(match.group(1)):,.0f} TL"

    return "İndirimli fiyat bulunamadı"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    price = get_price()
    send_telegram_message(f"Voyage Sorgun Güncel Fiyat: {price}")
    print("✅ Telegram’a gönderildi:", price)
