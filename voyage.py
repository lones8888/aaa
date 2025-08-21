from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests

BOT_TOKEN = "8064693875:AAFEHpkHFMTnqPno2gZB19FHAbyCMVtmWGQ"
CHAT_ID = "-1002950043362"

url = "https://www.etstur.com/Voyage-Sorgun"

# Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(5)  # sayfanın yüklenmesini bekle

# ekran görüntüsü kaydet
screenshot_path = "screenshot.png"
driver.save_screenshot(screenshot_path)
driver.quit()

# Telegram'a gönder
with open(screenshot_path, "rb") as img:
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={"chat_id": CHAT_ID, "caption": "Voyage Sorgun Güncel Fiyatlar"},
        files={"photo": img}
    )


