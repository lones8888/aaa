# -*- coding: utf-8 -*-
# okx_liquidity_bot.py
#
# KOŞUL (SHORT, simetrik LONG):
# 1) SON 15 mumda aşırı yükseliş (min→son_high >= SURGE_PCT)
# 2) Sinyal mumunda üst tarafta "likidite temizliği" (sweep):
#       high[t] > max(high[t-SWEEP_BACK : t])
# 3) Sweep'ten önce oluşmuş SON "untested low" bulunur (pivot low olup
#    kendi barından sonra sinyal mumuna kadar altına inilmemiş).
# 4) SİNYAL: aynı mumda close[t] < (untested low)  → Entry = o low
#    SL  = son SL_LOOKBACK mumun en yüksek high'ı
#    TP  = Entry - 2R * (SL - Entry)
#
# LONG tarafı simetrik (aşırı düşüş + altta sweep + untested high üstü kırılım)

import os, json, time, math, datetime as dt
from typing import Optional, Dict, List

import ccxt
import pandas as pd
import numpy as np
import requests

# ── TELEGRAM ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
TELEGRAM_CHAT_ID = "-1002950043362"

def send_telegram(text: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)

# ── PARAMS ────────────────────────────────────────────────────────────────────
TIMEFRAME       = "4h"
HISTORY_BARS    = 500
POLL_SEC        = 60

SURGE_LOOKBACK  = 15         # “aynı mumda” öncesi/etrafı kontrol penceresi
SURGE_PCT       = 0.20       # >= %20 hareket “aşırı” say
SWEEP_BACK      = 20         # sweep kontrol penceresi
PIV_L = 2                    # pivot L
PIV_R = 2                    # pivot R
SL_LOOKBACK     = 10         # SL = son 10 mumun high/low’u
RR              = 2.0        # TP = 2R

CACHE_FILE = "signal_cache.json"

# ── YARDIMCI ──────────────────────────────────────────────────────────────────
def ts_str(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%d %H:%M")

def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_okx_symbols(ex: ccxt.okx) -> List[str]:
    markets = ex.load_markets()
    syms = []
    for sym, m in markets.items():
        if not m.get("active", False):
            continue
        if m.get("contract", False) and m.get("quote") == "USDT":
            syms.append(sym)
    return sorted(set(syms))

def fetch_df(ex: ccxt.okx, symbol: str, limit: int) -> pd.DataFrame:
    ohlcv = ex.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["ts","open","high","low","close","vol"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df

def pivot_flags(series: pd.Series, L: int, R: int, high_pivot: bool) -> np.ndarray:
    n = len(series)
    out = np.zeros(n, dtype=bool)
    for i in range(L, n-R):
        window = series.iloc[i-L:i+R+1]
        if high_pivot:
            if series.iloc[i] == window.max() and series.iloc[i] > series.iloc[i-1] and series.iloc[i] >= series.iloc[i+1]:
                out[i] = True
        else:
            if series.iloc[i] == window.min() and series.iloc[i] < series.iloc[i-1] and series.iloc[i] <= series.iloc[i+1]:
                out[i] = True
    return out

# ── SİNYAL MANTIKLARI ────────────────────────────────────────────────────────
def detect_short(df: pd.DataFrame) -> Optional[Dict]:
    # son kapalı bar
    t = len(df) - 1
    if t < max(SURGE_LOOKBACK, SWEEP_BACK) + 5:
        return None

    # 1) aşırı yükseliş (son 15 mum)
    win = df.iloc[t-SURGE_LOOKBACK+1 : t+1]
    lo = win["low"].min()
    hi = win["high"].max()
    if lo <= 0: 
        return None
    if (hi - lo) / lo < SURGE_PCT:
        return None

    # 2) üstte sweep (aynı bar)
    window_max = df["high"].iloc[t-SWEEP_BACK:t].max()
    if df["high"].iloc[t] <= window_max:
        return None

    # 3) sweep'ten ÖNCE oluşmuş SON "untested low"
    #    (pivot low + pivot sonrası sinyal barına kadar low bu seviyenin altına inmedi)
    pivL = pivot_flags(df["low"], PIV_L, PIV_R, high_pivot=False)
    # yalnızca sweep barından önce olan pivotlar
    cand_ids = np.where(pivL[:t])[0]
    cand_ids = cand_ids[cand_ids < t]  # kesin
    if cand_ids.size == 0:
        return None

    # sondan geriye doğru ilk "untested low"u bul
    utl_idx = None
    for i in cand_ids[::-1]:
        level = df["low"].iloc[i]
        # pivot barından sonra t barına kadar bu seviyenin altı TEST EDİLMEMİŞ olmalı
        if df["low"].iloc[i+1:t].min() > level:
            utl_idx = i
            break
    if utl_idx is None:
        return None

    utl = float(df["low"].iloc[utl_idx])

    # 4) tetik: aynı mumda bu untested low altına kapanış
    if df["close"].iloc[t] >= utl:
        return None

    entry = utl
    sl = float(df["high"].iloc[t-SL_LOOKBACK+1 : t+1].max())
    if sl <= entry:
        return None
    tp = entry - RR * (sl - entry)

    return {
        "side": "SHORT",
        "entry": entry,
        "sl": sl,
        "tp": float(tp),
        "price_now": float(df["close"].iloc[t]),
        "sweep_ts": ts_str(df["ts"].iloc[t]),
        "untested_ts": ts_str(df["ts"].iloc[utl_idx]),
        "bar_ts": ts_str(df["ts"].iloc[t]),
    }

def detect_long(df: pd.DataFrame) -> Optional[Dict]:
    t = len(df) - 1
    if t < max(SURGE_LOOKBACK, SWEEP_BACK) + 5:
        return None

    # 1) aşırı düşüş (son 15 mum)
    win = df.iloc[t-SURGE_LOOKBACK+1 : t+1]
    hi = win["high"].max()
    lo = win["low"].min()
    if hi <= 0:
        return None
    if (hi - lo) / hi < SURGE_PCT:
        return None

    # 2) altta sweep (aynı bar)
    window_min = df["low"].iloc[t-SWEEP_BACK:t].min()
    if df["low"].iloc[t] >= window_min:
        return None

    # 3) sweep'ten ÖNCE oluşmuş SON "untested high"
    pivH = pivot_flags(df["high"], PIV_L, PIV_R, high_pivot=True)
    cand_ids = np.where(pivH[:t])[0]
    cand_ids = cand_ids[cand_ids < t]
    if cand_ids.size == 0:
        return None

    uth_idx = None
    for i in cand_ids[::-1]:
        level = df["high"].iloc[i]
        # pivot barından sonra t barına kadar BU seviyenin üstü TEST EDİLMEMİŞ olmalı
        if df["high"].iloc[i+1:t].max() < level:
            uth_idx = i
            break
    if uth_idx is None:
        return None

    uth = float(df["high"].iloc[uth_idx])

    # 4) tetik: aynı mumda bu untested high ÜZERİNE kapanış
    if df["close"].iloc[t] <= uth:
        return None

    entry = uth
    sl = float(df["low"].iloc[t-SL_LOOKBACK+1 : t+1].min())
    if sl >= entry:
        return None
    tp = entry + RR * (entry - sl)

    return {
        "side": "LONG",
        "entry": entry,
        "sl": sl,
        "tp": float(tp),
        "price_now": float(df["close"].iloc[t]),
        "sweep_ts": ts_str(df["ts"].iloc[t]),
        "untested_ts": ts_str(df["ts"].iloc[uth_idx]),
        "bar_ts": ts_str(df["ts"].iloc[t]),
    }

def fmt(symbol: str, sig: Dict) -> str:
    if sig["side"] == "SHORT":
        return (
            f"📉 <b>Short</b> | <code>{symbol}</code>\n"
            f"TF: {TIMEFRAME}\n"
            f"➡️ Entry: <code>{sig['entry']:.10g}</code>\n"
            f"🔴 SL: <code>{sig['sl']:.10g}</code>\n"
            f"🎯 TP (2R): <code>{sig['tp']:.10g}</code>\n"
            f"💬 Price now: <code>{sig['price_now']:.10g}</code>\n"
            f"🧽 Sweep/Bar: {sig['sweep_ts']}  |  Untested: {sig['untested_ts']}"
        )
    else:
        return (
            f"📈 <b>Long</b> | <code>{symbol}</code>\n"
            f"TF: {TIMEFRAME}\n"
            f"➡️ Entry: <code>{sig['entry']:.10g}</code>\n"
            f"🔴 SL: <code>{sig['sl']:.10g}</code>\n"
            f"🎯 TP (2R): <code>{sig['tp']:.10g}</code>\n"
            f"💬 Price now: <code>{sig['price_now']:.10g}</code>\n"
            f"🧽 Sweep/Bar: {sig['sweep_ts']}  |  Untested: {sig['untested_ts']}"
        )

# ── ANA DÖNGÜ ────────────────────────────────────────────────────────────────
def main():
    cache = load_cache()
    ex = ccxt.okx({"enableRateLimit": True})

    symbols = get_okx_symbols(ex)
    print(f"{len(symbols)} OKX USDT perpetual taranacak.")
    # referans: BTC bar kapanışı ile tetikle
    ref_symbol = "BTC-USDT-SWAP"

    last_close_ts = None

    while True:
        try:
            ref = fetch_df(ex, ref_symbol, 50)
            cur_close_ts = int(ref["ts"].iloc[-1].timestamp()*1000)
            if last_close_ts == cur_close_ts:
                time.sleep(POLL_SEC)
                continue
            last_close_ts = cur_close_ts
            print("Yeni 4H kapanışı:", ts_str(ref["ts"].iloc[-1]))

            for sym in symbols:
                try:
                    df = fetch_df(ex, sym, HISTORY_BARS)
                    sig = detect_short(df)
                    if sig is None:
                        sig = detect_long(df)
                    if sig is None:
                        continue

                    key = f"{sym}|{sig['side']}|{cur_close_ts}"
                    if cache.get(key):
                        continue

                    msg = fmt(sym, sig)
                    print("ALARM:", sym, sig["side"])
                    send_telegram(msg)
                    cache[key] = "sent"
                    save_cache(cache)

                except Exception as se:
                    print("Symbol error:", sym, se)

        except Exception as e:
            print("Loop error:", e)

        time.sleep(POLL_SEC)

if __name__ == "__main__":
    main()
