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
    # Senin coin listen (otomatik -USDT-SWAP eklenecek)
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
LOOKBACK_MIN = 8
LOOKBACK_MAX = 100

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

        sequence = []
        for i in range(-lookback, 0):
            if lows[i] <= lowest:
                sequence.append(("low", i))
            if highs[i] >= highest:
                sequence.append(("high", i))

        if not sequence:
            continue

        first_event, idx = sequence[0]

        if first_event == "low" and highs[-1] >= highest:
            entry = highs[idx]
            sl = lows[idx]
            price = closes[-1]
            signal_key = ("LONG", entry, sl)
            if signal_key not in seen_signals:
                seen_signals.add(signal_key)
                results.append(
                    f"🟢 LONG {symbol} (Lookback {lookback})\nEntry: {entry}\nSL: {sl}\nPrice: {price}"
                )

        elif first_event == "high" and lows[-1] <= lowest:
            entry = lows[idx]
            sl = highs[idx]
            price = closes[-1]
            signal_key = ("SHORT", entry, sl)
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
