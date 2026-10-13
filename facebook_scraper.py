from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time
import json
import copy
import os
import re
from typing import Dict, Optional

class FacebookScraper:
    def __init__(self, email: str, password: str, proxy: Optional[Dict[str, str]] = None, headless=False, log_level=logging.INFO, debug=False):
        self.email = email
        self.password = password
        self.proxy = proxy
        self.headless = headless
        self.debug = debug
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

    def login(self, login_timeout=180):
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
            email_field = self.wait.until(EC.element_to_be_clickable((By.NAME, "email")))
            password_field = self.wait.until(EC.element_to_be_clickable((By.NAME, "pass")))
            
            email_field.send_keys(self.email)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            
            # Giriş kontrolü: Facebook "c_user" çerezini yalnızca giriş tamamlanınca oluşturur.
            # İki adımlı doğrulama / güvenlik kontrolü çıkarsa tarayıcıda elle tamamlamak için süre tanınır.
            self.logger.info(f"Girişin tamamlanması bekleniyor (en fazla {login_timeout} sn). "
                             "Doğrulama kodu istenirse tarayıcıda elle girin...")
            WebDriverWait(self.driver, login_timeout).until(
                lambda d: d.get_cookie("c_user") is not None
            )
            self.logger.info("Giriş başarılı!")
            return True

        except TimeoutException:
            self.logger.error(f"Giriş {login_timeout} sn içinde tamamlanmadı. "
                              f"Mevcut sayfa: {self.driver.current_url} (şifre hatalı ya da doğrulama tamamlanmadı)")
            return False
        except Exception as e:
            self.logger.error(f"Giriş hatası: {str(e)}")
            return False

    def scrape_profile(self, profile_url):
        try:
            self.logger.info(f"Profil verisi çekiliyor: {profile_url}")
            profile_url = profile_url.rstrip('/')
            self.driver.get(profile_url)
            time.sleep(3)

            # Temel bilgiler ve kişisel detaylar profil sayfasının kendisinden okunur
            profile_soup = self._get_soup('profil')

            profile_data = {
                'temel_bilgiler': self._parse_basic_info(profile_soup),
                'hakkinda': self._parse_about_info(profile_soup),
                'paylasimlar': self._get_posts(profile_url),
                'arkadaslar': self._get_friends(profile_url),
                'fotograflar': self._get_photos(profile_url),
                'cekilis_tarihi': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return profile_data

        except Exception as e:
            self.logger.error(f"Profil çekme hatası: {str(e)}")
            return None

    # Not: Facebook'un "x1yztbdb" gibi CSS sınıfları otomatik üretilir ve sık değişir.
    # Bu yüzden aşağıdaki seçiciler role, aria-label, data-ad-rendering-role ve başlıklar gibi
    # daha kalıcı özelliklere dayanır. Başlık metinleri Türkçe arayüze göredir (--lang=tr).

    def _main(self, soup):
        # Bildirim ve sohbet panelleri dışındaki ana içerik alanı
        return soup.find(attrs={'role': 'main'}) or soup

    def _section_by_heading(self, soup, heading_text, min_links=3):
        # Verilen başlığa (h2) sahip bölümü, içinde yeterince bağlantı olana kadar yukarı çıkarak bulur
        for heading in self._main(soup).find_all('h2'):
            if heading.get_text(strip=True) == heading_text:
                section = heading
                while section.parent is not None and len(section.find_all('a', href=True)) < min_links:
                    section = section.parent
                return section
        return None

    def _leaf_texts(self, element):
        # İç içe olmayan dir="auto" span metinlerini sırasıyla döndürür
        texts = []
        for span in element.find_all('span', attrs={'dir': 'auto'}):
            if span.find('span', attrs={'dir': 'auto'}):
                continue
            text = span.get_text(' ', strip=True)
            if text:
                texts.append(text)
        return texts

    def _parse_basic_info(self, soup):
        basic_info = {'isim': "Bulunamadı", 'profil_fotografi': "Bulunamadı", 'kapak_fotografi': "Bulunamadı"}
        try:
            main = self._main(soup)

            # Profil fotoğrafı, ana alandaki en büyük svg <image>; svg'nin aria-label'ı profil adıdır
            def image_size(image):
                match = re.search(r'height:\s*(\d+)px', image.get('style', ''))
                return int(match.group(1)) if match else 0
            images = [image for image in main.find_all('image') if image.get('xlink:href')]
            if images:
                profile_pic = max(images, key=image_size)
                basic_info['profil_fotografi'] = profile_pic['xlink:href']
                svg = profile_pic.find_parent('svg')
                if svg and svg.get('aria-label'):
                    basic_info['isim'] = svg['aria-label']

            if basic_info['isim'] == "Bulunamadı":
                name_element = main.find('h1')
                if name_element:
                    basic_info['isim'] = name_element.get_text(' ', strip=True)

            # Kapak fotoğrafı
            cover_pic = main.find('img', attrs={'data-imgperflogname': 'profileCoverPhoto'})
            if cover_pic and cover_pic.get('src'):
                basic_info['kapak_fotografi'] = cover_pic['src']

        except Exception as e:
            self.logger.error(f"Temel bilgi çekme hatası: {str(e)}")

        return basic_info

    def _parse_about_info(self, soup):
        about_info = {'kisisel_detaylar': [], 'yasadigi_yer': "Bulunamadı", 'memleket': "Bulunamadı", 'dogum_tarihi': "Bulunamadı"}
        try:
            section = None
            for heading in self._main(soup).find_all('h2'):
                if heading.get_text(strip=True) == 'Kişisel detaylar':
                    section = heading
                    while section.parent is not None and len(self._leaf_texts(section)) < 3:
                        section = section.parent
                    break
            if section is None:
                return about_info

            details = [text for text in self._leaf_texts(section)
                       if text != 'Kişisel detaylar' and not text.startswith('Daha fazla')]
            about_info['kisisel_detaylar'] = details

            for text in details:
                if text.endswith('yaşıyor'):
                    about_info['yasadigi_yer'] = re.sub(r"'?(da|de|ta|te)\s+yaşıyor$", '', text).strip()
                elif text.startswith('Memleketi'):
                    about_info['memleket'] = text[len('Memleketi'):].strip()

            birthday = section.find(attrs={'aria-label': re.compile(r'^Doğum günü')})
            if birthday:
                about_info['dogum_tarihi'] = birthday['aria-label'].split(',', 1)[-1].strip()

        except Exception as e:
            self.logger.error(f"Hakkında bilgisi çekme hatası: {str(e)}")

        return about_info

    def _get_posts(self, profile_url, post_limit=20, scroll_count=5):
        posts = []
        seen = set()
        try:
            self.driver.get(profile_url)
            time.sleep(3)

            # Facebook kaydırdıkça eski paylaşımları sayfadan kaldırır, bu yüzden her kaydırmada okunur
            for i in range(scroll_count + 1):
                page_source = self.driver.page_source
                if self.debug and i == 0:
                    self._dump_page('paylasimlar', page_source)
                for post in self._parse_posts(BeautifulSoup(page_source, 'html.parser')):
                    key = post['metin'] or post['baglanti']
                    if key and key not in seen:
                        seen.add(key)
                        posts.append(post)
                if len(posts) >= post_limit or i == scroll_count:
                    break
                self.scroll_page(1)

        except Exception as e:
            self.logger.error(f"Paylaşım çekme hatası: {str(e)}")

        return posts[:post_limit]

    def _parse_posts(self, soup):
        posts = []
        containers = []
        for profile_name in soup.find_all(attrs={'data-ad-rendering-role': 'profile_name'}):
            # Paylaşımın kapsayıcısı: yazar adından yukarı çıkıp yorum butonunu içeren ilk eleman
            container = profile_name
            while container.parent is not None and not container.find(attrs={'data-ad-rendering-role': 'comment_button'}):
                container = container.parent
            if container.parent is None or any(container is c for c in containers):
                continue
            containers.append(container)

        for container in containers:
            container = copy.copy(container)
            # Paylaşımın altındaki yorumları çıkar (role="article")
            for comment in container.find_all(attrs={'role': 'article'}):
                comment.decompose()

            text_parts = [div.get_text(' ', strip=True) for div in container.find_all('div', attrs={'dir': 'auto'})
                          if not div.find('div', attrs={'dir': 'auto'})]
            reactions, comments, shares = self._extract_counts(container)
            posts.append({
                'metin': '\n'.join(part for part in text_parts if part),
                'baglanti': self._extract_post_link(container),
                'begeni_sayisi': reactions,
                'yorum_sayisi': comments,
                'paylasim_sayisi': shares
            })
        return posts

    def _extract_post_link(self, post):
        for link in post.find_all('a', href=True):
            href = link['href']
            if re.search(r'/posts/|/videos/|/reel/|/photo|story_fbid|/permalink/', href) and 'comment_id' not in href:
                return href.split('&__cft__')[0].split('?__cft__')[0]
        return "Bulunamadı"

    def _parse_count(self, text):
        # "1,2 B", "3K", "1.5 Mn" gibi kısaltılmış sayıları tam sayıya çevirir
        match = re.match(r'([\d.,]+)\s*(B|K|Mn|M)?', text.strip(), re.IGNORECASE)
        if not match:
            return 0
        number, suffix = match.groups()
        multiplier = {'b': 1_000, 'k': 1_000, 'mn': 1_000_000, 'm': 1_000_000}.get((suffix or '').lower(), 1)
        if multiplier == 1:
            return int(re.sub(r'[.,]', '', number))
        return int(float(number.replace(',', '.')) * multiplier)

    def _extract_counts(self, post):
        # Beğen butonunun üstündeki satır sırasıyla ifade, yorum ve paylaşım sayılarını içerir: "39,3 B 7,9 B 2,9 B"
        anchor = post.find(attrs={'aria-label': re.compile(r'ifade bırakanları gör|See who reacted')})
        if anchor is None:
            return 0, 0, 0
        row = anchor
        numbers = []
        for _ in range(6):
            row = row.parent
            numbers = re.findall(r'\d[\d.,]*\s?(?:B|K|Mn|M)?\b', row.get_text(' ', strip=True))
            if len(numbers) >= 3 or row.find(attrs={'data-ad-rendering-role': 'like_button'}):
                break
        counts = [self._parse_count(n) for n in numbers[:3]]
        return tuple(counts + [0] * (3 - len(counts)))

    def _get_friends(self, profile_url, friend_limit=100):
        friends = []
        try:
            self.driver.get(f"{profile_url}/friends")
            time.sleep(2)
            self.scroll_page(5)

            friends = self._parse_friends(self._get_soup('arkadaslar'), profile_url)[:friend_limit]

        except Exception as e:
            self.logger.error(f"Arkadaş listesi çekme hatası: {str(e)}")

        return friends

    def _parse_friends(self, soup, profile_url):
        friends = []
        seen = set()
        section = self._section_by_heading(soup, 'Arkadaşlar', min_links=5)
        if section is None:
            return friends
        for link in section.find_all('a', href=True):
            name = link.get_text(' ', strip=True)
            href = link['href']
            if not name or not href.startswith('https://www.facebook.com/') or href.startswith(profile_url):
                continue
            # profile.php?id=... dışındaki adreslerden takip parametrelerini temizle
            if 'profile.php' not in href:
                href = href.split('?')[0]
            if href in seen:
                continue
            seen.add(href)
            friends.append({'isim': name, 'profil_linki': href})
        return friends

    def _get_photos(self, profile_url, photo_limit=50):
        photos = []
        try:
            self.driver.get(f"{profile_url}/photos")
            time.sleep(2)
            self.scroll_page(3)

            photos = self._parse_photos(self._get_soup('fotograflar'))[:photo_limit]

        except Exception as e:
            self.logger.error(f"Fotoğraf çekme hatası: {str(e)}")

        return photos

    def _parse_photos(self, soup):
        photos = []
        seen = set()
        section = self._section_by_heading(soup, 'Fotoğraflar', min_links=5)
        if section is None:
            return photos
        for link in section.find_all('a', href=True):
            image = link.find('img')
            if not re.search(r'/photo', link['href']) or image is None or not image.get('src'):
                continue
            if image['src'] in seen:
                continue
            seen.add(image['src'])
            photos.append({
                'gorsel': image['src'],
                'baglanti': link['href'],
                'aciklama': image.get('alt', '')
            })
        return photos

    def _get_soup(self, page_name):
        page_source = self.driver.page_source
        if self.debug:
            self._dump_page(page_name, page_source)
        return BeautifulSoup(page_source, 'html.parser')

    def _dump_page(self, page_name, page_source):
        # Debug modunda sayfanın HTML'ini ve ekran görüntüsünü kaydeder
        try:
            debug_dir = os.path.join('ciktilar', 'debug')
            os.makedirs(debug_dir, exist_ok=True)
            with open(os.path.join(debug_dir, f"{page_name}.html"), 'w', encoding='utf-8') as f:
                f.write(page_source)
            self.driver.save_screenshot(os.path.join(debug_dir, f"{page_name}.png"))
            self.logger.info(f"Debug: {page_name} sayfası kaydedildi ({self.driver.current_url})")
        except Exception as e:
            self.logger.error(f"Debug kaydetme hatası: {str(e)}")

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