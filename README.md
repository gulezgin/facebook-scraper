# Facebook Profil Veri Kazıyıcı (Facebook Profile Scraper)

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-brightgreen)](https://www.selenium.dev/)
[![BeautifulSoup](https://img.shields.io/badge/beautifulsoup4-4.9+-yellow)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Bu proje, Facebook profillerinden veri çekmek için geliştirilmiş gelişmiş bir Python kazıyıcıdır. Selenium ve BeautifulSoup kullanarak, herkese açık Facebook profillerinden çeşitli bilgileri otomatik olarak toplar.

## 🌟 Özellikler

- **Otomatik Giriş:** Facebook hesabınıza otomatik olarak giriş yapar.
- **Kapsamlı Profil Veri Kazıma:** Aşağıdaki verileri çeker:
    - Temel bilgiler (isim, profil fotoğrafı, kapak fotoğrafı)
    - Hakkında bilgileri (iş, eğitim, yaşadığı yer vb.)
    - Son paylaşımlar (metin, tarih, beğeni sayısı, yorum sayısı)
    - Arkadaş listesi (isim, profil bağlantısı)
    - Fotoğraflar (galeri bağlantıları)
- **Proxy Desteği:** HTTP ve SOCKS5 proxy'leri ile IP adresinizi gizleyerek anonim kazıma yapabilirsiniz.
- **Proxy Rotasyonu:** Birden fazla proxy kullanarak engellenme riskini azaltır.
- **Detaylı Loglama:** Hata ayıklama ve izleme için kapsamlı log kayıtları tutar.
- **JSON Çıktı:** Verileri kolayca işlenebilir JSON formatında kaydeder.
- **Çoklu Profil Desteği:** Aynı anda birden fazla profilin verilerini çekebilirsiniz.
- **Headless Mod:** Arka planda çalışarak kaynak tüketimini azaltır.
- **Kullanıcı Dostu:** Kolay kurulum ve yapılandırma ile hızlıca kullanmaya başlayabilirsiniz.

## 🛠️ Kurulum

1.  **Depoyu Klonlayın:**

    ```bash
    git clone https://github.com/kullaniciadi/facebook-scraper.git
    cd facebook-scraper
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Chrome Tarayıcısını Kurun:**

    -   Eğer sisteminizde Chrome tarayıcısı yüklü değilse, [buradan](https://www.google.com/chrome/) indirebilirsiniz.

4.  **Facebook Giriş Bilgilerinizi ve Proxy Ayarlarınızı Yapılandırın:**

    -   `main.py` dosyasını açın ve aşağıdaki yapılandırma ayarlarını güncelleyin:

        ```python
        config = {
            'email': 'your_email@example.com',
            'password': 'your_password',
            'headless': False,  # Arka planda çalıştırmak için True yapın
            'log_level': logging.INFO
        }
        ```

## ⚙️ Kullanım

1.  **Proxy Listesini Güncelleyin (Opsiyonel):**

    -   `main.py` dosyasında `get_proxy_list()` fonksiyonunu bulun ve proxy listenizi ekleyin:

        ```python
        def get_proxy_list():
            return [
                {
                    "http": "http://proxy1.example.com:8080",
                    "username": "user1",
                    "password": "pass1"
                },
                # Daha fazla proxy ekleyin
            ]
        ```

2.  **Çekmek İstediğiniz Profilleri Ekleyin:**

    -   `main.py` dosyasında `profiles` listesini bulun ve profil URL'lerini ekleyin:

        ```python
        profiles = [
            "https://www.facebook.com/zuck",
            # Diğer profil URL'lerini ekleyin
        ]
        ```

3.  **Kazıyıcıyı Çalıştırın:**

    ```bash
    python main.py
    ```

## 📂 Çıktılar

Veriler, `ciktilar` klasörüne JSON formatında kaydedilir. Her kazıma işlemi için benzersiz bir dosya adı oluşturulur:

JSON çıktı formatı örneği:
json
{
"temel_bilgiler": {
"isim": "Mark Zuckerberg",
"profil_fotografi": "https://example.com/profile.jpg",
"kapak_fotografi": "https://example.com/cover.jpg"
},
"hakkinda": {
"calisma_egitim": ["CEO at Meta", "Studied at Harvard University"],
"yasadigi_yer": "Menlo Park, California"
},
"paylasimlar": [
{
"metin": "Hello world!",
"tarih": "2024-03-01",
"begeni_sayisi": 1000,
"yorum_sayisi": 500
}
],
"arkadaslar": [
{
"isim": "Friend 1",
"profil_linki": "https://www.facebook.com/friend1"
}
],
"fotograflar": ["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"],
"cekilis_tarihi": "2024-03-01 12:34:56"
}


## ⚠️ Güvenlik ve Yasal Uyarılar

-   Bu aracı kullanırken Facebook'un kullanım koşullarına uyun.
-   Kişisel verilerin korunması yasalarına saygı gösterin.
-   Aşırı kullanımdan kaçının, aksi takdirde Facebook hesabınız askıya alınabilir.
-   Güvenilir proxy servisleri kullanın.

## 💡 İpuçları ve Öneriler

-   **Güvenilir Proxy Servisleri Kullanın:** Ücretsiz proxy'ler genellikle yavaş ve güvenilmezdir.
-   **Headless Modu Etkinleştirin:** `headless: True` ayarını kullanarak arka planda çalıştırın.
-   **İstek Sıklığını Sınırlayın:** Facebook'un bot algılama sistemlerinden kaçınmak için istekler arasında gecikmeler ekleyin.
-   **Proxy Rotasyonu Yapın:** Farklı IP adresleri kullanarak engellenme olasılığını azaltın.
-   **Logları İzleyin:** Hataları ve sorunları tespit etmek için log dosyalarını düzenli olarak kontrol edin.

## 🤝 Katkıda Bulunma

1.  Depoyu çatallayın (Fork).
2.  Yeni bir özellik dalı oluşturun (`git checkout -b feature/YeniOzellik`).
3.  Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`).
4.  Dalınızı gönderin (`git push origin feature/YeniOzellik`).
5.  Çekme isteği (Pull Request) oluşturun.

##  Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.

## 📧 İletişim

Sorularınız veya önerileriniz için bir sorun (Issue) oluşturabilir veya aşağıdaki kanallardan bana ulaşabilirsiniz:

-   E-posta: ornek@email.com
-   Twitter: [@kullaniciadi](https://twitter.com/kullaniciadi)

---

Umarım bu kazıyıcı işinize yarar! Herhangi bir sorunla karşılaşırsanız, lütfen benimle iletişime geçmekten çekinmeyin.