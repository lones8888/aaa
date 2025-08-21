import os
import re
import requests
from playwright.sync_api import sync_playwright

URL = "https://www.etstur.com/Voyage-Sorgun?check_in=06.09.2026&check_out=11.09.2026&adult_1=2&child_1=0"


def extract_numeric_price(raw_price_text: str) -> str:
    digits = re.findall(r"\d+", raw_price_text)
    if not digits:
        return ""
    return "".join(digits)


def get_price() -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="tr-TR",
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle", timeout=90000)

        selector = "h2[data-test-id='price']"
        page.wait_for_selector(selector, state="visible", timeout=90000)
        raw_text = page.locator(selector).inner_text().strip()

        context.close()
        browser.close()

    numeric = extract_numeric_price(raw_text)
    if numeric:
        return f"{raw_text} (≈ {numeric} TL)"
    return raw_text or "Fiyat bulunamadı"


def send_telegram_message(message: str) -> None:
    bot_token = os.environ.get("BOT_TOKEN", "")
    chat_id = os.environ.get("CHAT_ID", "")
    if not bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload, timeout=30)
    except Exception:
        pass


if __name__ == "__main__":
    price = get_price()
    send_telegram_message(f"Voyage Sorgun Güncel Fiyat: {price}")
