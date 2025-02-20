from facebook_scraper import FacebookScraper
import logging
from datetime import datetime
from typing import List, Dict
import random

def get_proxy_list() -> List[Dict[str, str]]:
    """
    Proxy listesini döndürür. Bu örnekte statik bir liste kullanılmıştır.
    Gerçek uygulamada proxy'leri bir servisten veya dosyadan okuyabilirsiniz.
    """
    return [
        {
            "http": "http://proxy1.example.com:8080",
            "username": "user1",
            "password": "pass1"
        },
        {
            "socks5": "proxy2.example.com:1080",
            "username": "user2",
            "password": "pass2"
        },
        # Daha fazla proxy ekleyebilirsiniz
    ]

def main():
    # Yapılandırma
    config = {
        'email': 'your_email@example.com',
        'password': 'your_password',
        'headless': False,
        'log_level': logging.INFO
    }
    
    # Proxy listesini al
    proxy_list = get_proxy_list()
    
    # Çekilecek profiller
    profiles = [
        "https://www.facebook.com/zuck",
        # Diğer profil URL'lerini ekleyin
    ]
    
    for profile_url in profiles:
        success = False
        retry_count = 0
        max_retries = 3
        
        while not success and retry_count < max_retries:
            try:
                # Rastgele bir proxy seç
                current_proxy = random.choice(proxy_list) if proxy_list else None
                
                # Scraper'ı başlat
                scraper = FacebookScraper(
                    email=config['email'],
                    password=config['password'],
                    proxy=current_proxy,
                    headless=config['headless'],
                    log_level=config['log_level']
                )
                
                try:
                    # Facebook'a giriş yap
                    if scraper.login():
                        profile_data = scraper.scrape_profile(profile_url)
                        
                        if profile_data:
                            # Benzersiz dosya adı oluştur
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"facebook_data_{timestamp}.json"
                            
                            # Verileri kaydet
                            scraper.save_to_file(profile_data, filename)
                            success = True
                            
                except Exception as e:
                    logging.error(f"Veri çekme hatası: {str(e)}")
                    retry_count += 1
                    
                finally:
                    scraper.close()
                    
            except Exception as e:
                logging.error(f"Proxy bağlantı hatası: {str(e)}")
                retry_count += 1
                
        if not success:
            logging.error(f"Profil için maksimum deneme sayısına ulaşıldı: {profile_url}")

if __name__ == "__main__":
    main() 