import requests
import pandas as pd

# === TELEGRAM ===
BOT_TOKEN = "8295198129:AAGwdBjPNTZbBoVoLYCP8pUxeX7ZrfT7j_8"
CHAT_ID = "-1001660662034"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# === OKX ===
BASE_URL = "https://www.okx.com"

def get_usdt_pairs():
    coins = [
        "POPCAT","ARKM","LDO","PENGU","DOGE","NEAR","APT","BTC","HYPE","ETH",
        "XRP","OP","ARB","LTC","VINE","KAITO","MEME","LINK","MOVE","EIGEN",
        "BONK","PUMP","INJ","FARTCOIN","FLOKI","PNUT","JUP","NEIRO","MOODENG",
        "STABLE.C.D","SOL","BNB"
    ]
    return [f"{coin}-USDT-SWAP" for coin in coins]

def get_ohlcv(symbol, bar="4H", limit=120):
    url = f"{BASE_URL}/api/v5/market/candles"
    params = {"instId": symbol, "bar": bar, "limit": limit}
    r = requests.get(url, params=params)
    data = r.json()
    if "data" not in data: 
        return None
    df = pd.DataFrame(data["data"], columns=["ts","o","h","l","c","vol","volCcy","volCcyQuote","confirm"])
    df = df.astype({"o":float,"h":float,"l":float,"c":float})
    df = df.sort_values("ts")
    return df

# === STRATEJİ ===
LOOKBACK_MIN = 10
LOOKBACK_MAX = 25

def strategy(symbol):
    df = get_ohlcv(symbol)
    if df is None: 
        return None

    highs = df["h"].values
    lows  = df["l"].values
    closes = df["c"].values

    results = []
    seen_signals = set()

    for lookback in range(LOOKBACK_MIN, LOOKBACK_MAX + 1):
        if len(highs) < lookback:
            continue

        highest = max(highs[-lookback:])
        lowest  = min(lows[-lookback:])

        # === LONG SETUP ===
        lowest_idx = None
        for i in range(-lookback, 0):
            if lows[i] == lowest:
                lowest_idx = i  # son oluşan lowest bar
        if lowest_idx is not None:
            # lowest'tan sonra oluşan en yüksek değeri bul
            post_lowest_high = max(highs[lowest_idx:])  
            # son fiyat bu değerin üstüne çıkarsa MSB olur
            if closes[-1] > post_lowest_high and lowest_idx < len(highs) - 1:
                entry = highs[lowest_idx]   # sweep mumunun high’ı
                sl = lows[lowest_idx]       # sweep mumunun low’u
                price = closes[-1]
                signal_key = ("LONG", entry, sl, lookback)
                if signal_key not in seen_signals:
                    seen_signals.add(signal_key)
                    results.append(
                        f"🟢 LONG {symbol} (Lookback {lookback})\nEntry: {entry}\nSL: {sl}\nPrice: {price}"
                    )

        # === SHORT SETUP ===
        highest_idx = None
        for i in range(-lookback, 0):
            if highs[i] == highest:
                highest_idx = i  # son oluşan highest bar
        if highest_idx is not None:
            # highest’tan sonra oluşan en düşük değeri bul
            post_highest_low = min(lows[highest_idx:])  
            # son fiyat bu değerin altına inerse MSB olur
            if closes[-1] < post_highest_low and highest_idx < len(lows) - 1:
                entry = lows[highest_idx]   # sweep mumunun low’u
                sl = highs[highest_idx]     # sweep mumunun high’ı
                price = closes[-1]
                signal_key = ("SHORT", entry, sl, lookback)
                if signal_key not in seen_signals:
                    seen_signals.add(signal_key)
                    results.append(
                        f"🔴 SHORT {symbol} (Lookback {lookback})\nEntry: {entry}\nSL: {sl}\nPrice: {price}"
                    )

    if results:
        return "\n\n".join(results)
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
