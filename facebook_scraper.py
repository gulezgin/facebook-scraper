from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time
import json
import os
import re
from typing import Dict, Optional

class FacebookScraper:
    def __init__(self, email: str, password: str, proxy: Optional[Dict[str, str]] = None, headless=False, log_level=logging.INFO):
        self.email = email
        self.password = password
        self.proxy = proxy
        self.headless = headless
        self.setup_logging(log_level)
        self.setup_driver()
        
    def setup_logging(self, log_level):
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('facebook_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--lang=tr")
            
            # Proxy ayarlarını ekle
            if self.proxy:
                if 'http' in self.proxy:
                    chrome_options.add_argument(f'--proxy-server={self.proxy["http"]}')
                elif 'socks5' in self.proxy:
                    chrome_options.add_argument(f'--proxy-server=socks5://{self.proxy["socks5"]}')
                
                # Proxy kimlik doğrulama bilgileri varsa
                if 'username' in self.proxy and 'password' in self.proxy:
                    chrome_options.add_argument(f'--proxy-auth={self.proxy["username"]}:{self.proxy["password"]}')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 10)
            
            # Proxy bağlantısını test et
            if self.proxy:
                self.logger.info("Proxy bağlantısı test ediliyor...")
                self.driver.get("https://api.ipify.org?format=json")
                self.logger.info(f"Mevcut IP: {self.driver.page_source}")
            
        except Exception as e:
            self.logger.error(f"Sürücü başlatma hatası: {str(e)}")
            raise

    def scroll_page(self, scroll_count=5):
        for _ in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    def login(self):
        try:
            self.logger.info("Facebook'a giriş yapılıyor...")
            self.driver.get("https://www.facebook.com")
            
            # Çerez uyarısını kabul et
            try:
                cookie_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-cookiebanner='accept_button']"))
                )
                cookie_button.click()
            except:
                self.logger.warning("Çerez uyarısı bulunamadı")
            
            # Giriş yap
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "pass")))
            
            email_field.send_keys(self.email)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            
            # Giriş kontrolü
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='main']")))
            self.logger.info("Giriş başarılı!")
            return True
            
        except Exception as e:
            self.logger.error(f"Giriş hatası: {str(e)}")
            return False

    def scrape_profile(self, profile_url):
        try:
            self.logger.info(f"Profil verisi çekiliyor: {profile_url}")
            self.driver.get(profile_url)
            time.sleep(3)
            
            profile_data = {
                'temel_bilgiler': self._get_basic_info(),
                'hakkinda': self._get_about_info(),
                'paylasimlar': self._get_posts(),
                'arkadaslar': self._get_friends(),
                'fotograflar': self._get_photos(),
                'cekilis_tarihi': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Profil çekme hatası: {str(e)}")
            return None

    def _get_basic_info(self):
        basic_info = {}
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Profil adı
            name_element = soup.find('h1')
            basic_info['isim'] = name_element.text if name_element else "Bulunamadı"
            
            # Profil fotoğrafı
            try:
                profile_pic = soup.find('image', {'class': 'x1b0d499 xaj1gnb'})
                basic_info['profil_fotografi'] = profile_pic.get('xlink:href') if profile_pic else "Bulunamadı"
            except:
                basic_info['profil_fotografi'] = "Bulunamadı"
                
            # Kapak fotoğrafı
            try:
                cover_pic = soup.find('img', {'class': 'x1ey2m1c'})
                basic_info['kapak_fotografi'] = cover_pic.get('src') if cover_pic else "Bulunamadı"
            except:
                basic_info['kapak_fotografi'] = "Bulunamadı"
                
        except Exception as e:
            self.logger.error(f"Temel bilgi çekme hatası: {str(e)}")
            
        return basic_info

    def _get_about_info(self):
        about_info = {}
        try:
            # Hakkında sayfasına git
            self.driver.get(f"{self.driver.current_url}/about")
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Çalışma ve eğitim bilgileri
            work_education = soup.find_all('div', {'class': 'x1hq5gj4'})
            about_info['calisma_egitim'] = [item.get_text(strip=True) for item in work_education]
            
            # Yaşadığı yer
            location = soup.find('div', {'class': 'x1hq5gj4 x1otrzb0'})
            about_info['yasadigi_yer'] = location.get_text(strip=True) if location else "Bulunamadı"
            
        except Exception as e:
            self.logger.error(f"Hakkında bilgisi çekme hatası: {str(e)}")
            
        return about_info

    def _get_posts(self, post_limit=20):
        posts = []
        try:
            self.driver.get(f"{self.driver.current_url}")
            time.sleep(2)
            self.scroll_page(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            post_elements = soup.find_all('div', {'class': 'x1yztbdb'})
            
            for post in post_elements[:post_limit]:
                post_data = {
                    'metin': post.get_text(strip=True),
                    'tarih': self._extract_post_date(post),
                    'begeni_sayisi': self._extract_likes(post),
                    'yorum_sayisi': self._extract_comments(post)
                }
                posts.append(post_data)
                
        except Exception as e:
            self.logger.error(f"Paylaşım çekme hatası: {str(e)}")
            
        return posts

    def _get_friends(self, friend_limit=100):
        friends = []
        try:
            self.driver.get(f"{self.driver.current_url}/friends")
            time.sleep(2)
            self.scroll_page(5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            friend_elements = soup.find_all('div', {'class': 'x1dm5mii'})
            
            for friend in friend_elements[:friend_limit]:
                friend_data = {
                    'isim': friend.find('span').text if friend.find('span') else "Bulunamadı",
                    'profil_linki': friend.find('a')['href'] if friend.find('a') else "Bulunamadı"
                }
                friends.append(friend_data)
                
        except Exception as e:
            self.logger.error(f"Arkadaş listesi çekme hatası: {str(e)}")
            
        return friends

    def _get_photos(self, photo_limit=50):
        photos = []
        try:
            self.driver.get(f"{self.driver.current_url}/photos")
            time.sleep(2)
            self.scroll_page(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            photo_elements = soup.find_all('img', {'class': 'x1b0d499'})
            
            for photo in photo_elements[:photo_limit]:
                if 'src' in photo.attrs:
                    photos.append(photo['src'])
                
        except Exception as e:
            self.logger.error(f"Fotoğraf çekme hatası: {str(e)}")
            
        return photos

    def save_to_file(self, data, filename):
        try:
            os.makedirs('ciktilar', exist_ok=True)
            filepath = os.path.join('ciktilar', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.logger.info(f"Veriler başarıyla kaydedildi: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Dosya kaydetme hatası: {str(e)}")

    def close(self):
        try:
            self.driver.quit()
            self.logger.info("Tarayıcı kapatıldı")
        except:
            self.logger.warning("Tarayıcı kapatılırken hata oluştu") 