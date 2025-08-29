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

        # === LONG şartı ===
        # önce lowest oluşmalı, sonra fiyat highest üstüne çıkmalı
        if lows[-lookback:].min() == lowest and closes[-1] > highest:
            entry = highest
            sl = lowest
            price = closes[-1]
            signal_key = ("LONG", entry, sl, lookback)
            if signal_key not in seen_signals:
                seen_signals.add(signal_key)
                results.append(
                    f"🟢 LONG {symbol} (Lookback {lookback})\nEntry: {entry}\nSL: {sl}\nPrice: {price}"
                )

        # === SHORT şartı ===
        # önce highest oluşmalı, sonra fiyat lowest altına inmeli
        if highs[-lookback:].max() == highest and closes[-1] < lowest:
            entry = lowest
            sl = highest
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
