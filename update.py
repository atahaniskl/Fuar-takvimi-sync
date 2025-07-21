import os
import shutil
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException

# İndirme klasörünü ve hedef dosya yolunu ayarla
DOWNLOAD_DIR = os.path.join(os.getcwd(), "indirilen_takvimler")
TARGET_FILE = os.path.join(os.getcwd(), "fuar_takvimi.xlsx")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Chrome seçeneklerini ayarla
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
})
chrome_options.add_argument("--headless")

# WebDriver başlatmayı dene ve sürüm uyumsuzluğu hatasını yakala
try:
    driver = webdriver.Chrome(options=chrome_options)
except SessionNotCreatedException as e:
    print("Hata: ChromeDriver ile Chrome tarayıcınızın sürümü uyuşmuyor.")
    print("Lütfen Chrome ve ChromeDriver sürümlerinizi güncelleyin.")
    print(f"Detay: {e}")
    exit(1)
except WebDriverException as e:
    print("WebDriver başlatılamadı. Lütfen ChromeDriver ve Chrome kurulumunuzu kontrol edin.")
    print(f"Detay: {e}")
    exit(1)

try:
    driver.get("https://fuarlar.tobb.org.tr/FuarTakvimi")
    time.sleep(10)  # Sayfanın yüklenmesi

    # Excel'e kaydet butonunu bul ve tıkla
    download_button = driver.find_element(By.XPATH, "//button[.//span[contains(text(), \"Excel'e Kaydet\")]]")
    download_button.click()
    print("Excel'e Kaydet butonuna tıklandı. Dosyanın indirilmesi bekleniyor...")

    time.sleep(10)  # Dosyanın indirilmesini bekle

    # İndirilen .xlsx dosyalarını bul
    files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".xlsx")]
    if not files:
        print("İndirme başarısız: Dosya bulunamadı.")
    else:
        # En yeni indirilen dosyayı bul
        files_full_path = [os.path.join(DOWNLOAD_DIR, f) for f in files]
        latest_file = max(files_full_path, key=os.path.getctime)

        # Dosyayı yeniden adlandır gün adı ile
        today_str = datetime.date.today().isoformat()
        renamed_file = os.path.join(DOWNLOAD_DIR, f"{today_str}.xlsx")
        os.rename(latest_file, renamed_file)

        # Eski indirilenleri sil
        for file_path in files_full_path:
            if file_path != renamed_file:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"⚠️ {file_path} silinemedi: {e}")

        # fuar takvimi dosyasına indirilen dosyayı kopyala
        shutil.copyfile(renamed_file, TARGET_FILE)
        print(f"✅ {TARGET_FILE} dosyası başarıyla güncellendi.")

finally:
    driver.quit()
