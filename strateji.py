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
    url = f"{BASE_URL}/api/v5/public/instruments"
    params = {"instType": "SWAP"}   # SWAP pariteleri
    r = requests.get(url, params=params)
    data = r.json()
    pairs = [x["instId"] for x in data["data"] if x["instId"].endswith("-USDT-SWAP")]
    return pairs

def get_ohlcv(symbol, bar="4H", limit=120):   # yeterli mum al (80+ güvenlik payı)
    url = f"{BASE_URL}/api/v5/market/candles"
    params = {"instId": symbol, "bar": bar, "limit": limit}
    r = requests.get(url, params=params)
    data = r.json()
    if "data" not in data: return None
    df = pd.DataFrame(data["data"], columns=["ts","o","h","l","c","vol","volCcy","volCcyQuote","confirm"])
    df = df.astype({"o":float,"h":float,"l":float,"c":float})
    df = df.sort_values("ts")  # zaman sırası
    return df

# === STRATEJİ ===
LOOKBACK_MIN = 10   # burayı sen ayarlıyorsun
LOOKBACK_MAX = 80   # burayı da

def strategy(symbol):
    df = get_ohlcv(symbol)
    if df is None: 
        return None

    highs = df["h"].values
    lows  = df["l"].values
    closes = df["c"].values

    results = []  # tüm sinyalleri topla
    seen_signals = set()  # aynı entry/sl sinyali tekrar göndermemek için

    for lookback in range(LOOKBACK_MIN, LOOKBACK_MAX + 1):
        if len(highs) < lookback:   # yeterli mum yoksa atla
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
        return "\n\n".join(results)  # tüm benzersiz sinyalleri gönder

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
