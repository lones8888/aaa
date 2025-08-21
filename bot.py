import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# --- Telegram bilgileri (gizli değil, direkt kod içinde) ---
BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"
# ----------------------------------------------------------

def send_photo_to_telegram(photo_path, caption="Voyage Sorgun Güncel Görünüm"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as photo:
        response = requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"photo": photo},
        )
    print("Telegram yanıtı:", response.text)

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1280,1024")

    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=chrome_options)

    try:
        url = "https://www.etstur.com/Voyage-Sorgun"  
        driver.get(url)
        time.sleep(5)  

        screenshot_path = "voyage.png"
        driver.save_screenshot(screenshot_path)

        send_photo_to_telegram(screenshot_path)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

