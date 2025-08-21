import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"
URL = "https://www.etstur.com/Voyage-Sorgun?check_in=2026-09-06&check_out=2026-09-11&adult_1=2&child_1=0"

def take_screenshot(url, filename="screenshot.png"):
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,2000")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(8)  # sayfanın tamamen yüklenmesi için biraz bekle
    driver.save_screenshot(filename)
    driver.quit()
    return filename

def send_photo(file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(file_path, "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": photo})

if __name__ == "__main__":
    img = take_screenshot(URL)
    send_photo(img)
    print("✅ Screenshot alındı ve Telegram’a gönderildi!")
