import requests
import pandas as pd

# === TELEGRAM ===
BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# === OKX ===
BASE_URL = "https://www.okx.com"

def get_usdt_pairs():
    url = f"{BASE_URL}/api/v5/public/instruments"
    params = {"instType": "SWAP"}   # SWAP pariteleri
    r = requests.get(url, params=params)
    data = r.json()
    pairs = [x["instId"] for x in data["data"] if x["instId"].endswith("-USDT-SWAP")]
    return pairs

def get_ohlcv(symbol, bar="4H", limit=70):   # 70 mum al
    url = f"{BASE_URL}/api/v5/market/candles"
    params = {"instId": symbol, "bar": bar, "limit": limit}
    r = requests.get(url, params=params)
    data = r.json()
    if "data" not in data: return None
    df = pd.DataFrame(data["data"], columns=["ts","o","h","l","c","vol","volCcy","volCcyQuote","confirm"])
    df = df.astype({"o":float,"h":float,"l":float,"c":float})
    df = df.sort_values("ts")  # zaman sırası
    return df

def strategy(symbol):
    df = get_ohlcv(symbol)
    if df is None: 
        return None

    highs = df["h"].values
    lows = df["l"].values
    closes = df["c"].values

    highest = max(highs[-70:])   # 70 mum
    lowest = min(lows[-70:])

    sequence = []
    for i in range(-70, 0):
        if lows[i] <= lowest:
            sequence.append(("low", i))
        if highs[i] >= highest:
            sequence.append(("high", i))

    if not sequence:
        return None

    first_event, idx = sequence[0]

    if first_event == "low":
        if highs[-1] >= highest:
            entry = highs[idx]
            sl = lows[idx]
            price = closes[-1]
            return f"🟢 LONG {symbol}\nEntry: {entry}\nSL: {sl}\nPrice: {price}"
    elif first_event == "high":
        if lows[-1] <= lowest:
            entry = lows[idx]
            sl = highs[idx]
            price = closes[-1]
            return f"🔴 SHORT {symbol}\nEntry: {entry}\nSL: {sl}\nPrice: {price}"
    return None

if __name__ == "__main__":
    pairs = get_usdt_pairs()
    for sym in pairs:
        try:
            msg = strategy(sym)
            if msg:
                send_telegram(msg)
        except Exception as e:
            print(f"{sym} hata: {e}")
