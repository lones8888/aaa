import requests

# Telegram ayarları
BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"

# 🔹 Buraya tarayıcıda bulduğun API endpoint’ini yaz
API_URL = "https://www.etstur.com/services/api/gallery-detail"

# 🔹 Eğer GET parametreleri gerekiyorsa:
PARAMS = {
    "check_in": "2026-09-06",
    "check_out": "2026-09-11",
    "adult_1": 2,
    "child_1": 0,
    # gerekirse hotelId vb. parametreler
}

# 🔹 Eğer POST gerekiyorsa, bu kısmı body’ye göre değiştir
PAYLOAD = {
    "hotelId": 12345,  # gerçek hotelId değerini buraya koy
    "checkIn": "2026-09-06",
    "checkOut": "2026-09-11",
    "adults": 2,
    "children": 0
}

def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Eğer GET isteği ise:
    response = requests.get(API_URL, params=PARAMS, headers=headers)
    
    # Eğer POST gerekiyorsa yukarıdaki satırı yorum satırına al, şunu aç:
    # response = requests.post(API_URL, json=PAYLOAD, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        try:
            price = data["discountedPrice"]
            return f"{price:,.0f} TL"   # Örn: 112,800 TL
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

