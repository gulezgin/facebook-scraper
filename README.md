# Facebook Profil Veri Kazıyıcı (Facebook Profile Scraper)

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-brightgreen)](https://www.selenium.dev/)
[![BeautifulSoup](https://img.shields.io/badge/beautifulsoup4-4.9+-yellow)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Bu proje, Facebook profillerinden veri çekmek için geliştirilmiş gelişmiş bir Python kazıyıcıdır. Selenium ve BeautifulSoup kullanarak, herkese açık Facebook profillerinden çeşitli bilgileri otomatik olarak toplar.

## 🌟 Özellikler

- **Otomatik Giriş:** Facebook hesabınıza otomatik olarak giriş yapar. İki adımlı doğrulama veya güvenlik kontrolü çıkarsa tarayıcıda elle tamamlamanız için 180 saniye bekler.
- **Kapsamlı Profil Veri Kazıma:** Aşağıdaki verileri çeker:
    - Temel bilgiler (isim, profil fotoğrafı, kapak fotoğrafı)
    - Kişisel detaylar (yaşadığı yer, memleket, doğum tarihi)
    - Son paylaşımlar (metin, bağlantı, ifade / yorum / paylaşım sayısı)
    - Arkadaş listesi (isim, profil bağlantısı)
    - Fotoğraflar (görsel, bağlantı, açıklama)
- **Kalıcı Seçiciler:** Sık değişen otomatik CSS sınıfları yerine `role`, `aria-label`, `data-ad-rendering-role` ve bölüm başlıkları kullanılır.
- **Debug Modu:** Seçiciler bozulduğunda her sayfanın HTML'ini ve ekran görüntüsünü kaydederek inceleme imkânı sunar.
- **Proxy Desteği:** HTTP ve SOCKS5 proxy'leri ile kazıma yapabilirsiniz.
- **Proxy Rotasyonu:** Birden fazla proxy kullanarak engellenme riskini azaltır.
- **Detaylı Loglama:** Hata ayıklama ve izleme için kapsamlı log kayıtları tutar.
- **JSON Çıktı:** Verileri kolayca işlenebilir JSON formatında kaydeder.
- **Çoklu Profil Desteği:** Aynı anda birden fazla profilin verilerini çekebilirsiniz.
- **Headless Mod:** Arka planda çalışarak kaynak tüketimini azaltır.
- **Kullanıcı Dostu:** Kolay kurulum ve yapılandırma ile hızlıca kullanmaya başlayabilirsiniz.

## 🛠️ Kurulum

1.  **Depoyu Klonlayın:**

    ```bash
    git clone https://github.com/gulezgin/facebook-scraper.git
    cd facebook-scraper
    ```

2.  **Sanal Ortam Oluşturun ve Gerekli Kütüphaneleri Yükleyin:**

    ```bash
    python -m venv .venv
    .venv\Scriptsctivate        # Windows (macOS / Linux: source .venv/bin/activate)
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
            'log_level': logging.INFO,
            'debug': False      # True: sayfaların HTML'i ve ekran görüntüsü ciktilar/debug klasörüne kaydedilir
        }
        ```

    -   ⚠️ Giriş bilgilerinizi içeren `main.py` dosyasını GitHub'a göndermeyin.

## ⚙️ Kullanım

1.  **Proxy Listesini Güncelleyin (Opsiyonel):**

    -   `main.py` dosyasında `get_proxy_list()` fonksiyonunu bulun ve proxy listenizi ekleyin. Liste boşsa proxy kullanılmaz:

        ```python
        def get_proxy_list():
            return [
                {"http": "http://proxy1.example.com:8080"},
                {"socks5": "proxy2.example.com:1080"},
            ]
        ```

    -   Not: Chrome, kullanıcı adı / şifre gerektiren proxy'leri komut satırı ayarıyla desteklemez; kimlik doğrulamasız ya da IP yetkilendirmeli proxy kullanın.

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

Veriler, `ciktilar` klasörüne `facebook_data_YYYYAAGG_SSDDSS.json` adıyla JSON formatında kaydedilir.

JSON çıktı formatı örneği:

```json
{
    "temel_bilgiler": {
        "isim": "Mark Zuckerberg",
        "profil_fotografi": "https://scontent.xx.fbcdn.net/...",
        "kapak_fotografi": "https://scontent.xx.fbcdn.net/..."
    },
    "hakkinda": {
        "kisisel_detaylar": ["Palo Alto'da yaşıyor", "Memleketi Dobbs Ferry, New York", "14 Mayıs 1984"],
        "yasadigi_yer": "Palo Alto",
        "memleket": "Dobbs Ferry, New York",
        "dogum_tarihi": "14 Mayıs 1984"
    },
    "paylasimlar": [
        {
            "metin": "A decade of smoking meats",
            "baglanti": "https://www.facebook.com/4/videos/...",
            "begeni_sayisi": 55600,
            "yorum_sayisi": 8700,
            "paylasim_sayisi": 6700
        }
    ],
    "arkadaslar": [
        {
            "isim": "Arkadaş Adı",
            "profil_linki": "https://www.facebook.com/profile.php?id=..."
        }
    ],
    "fotograflar": [
        {
            "gorsel": "https://scontent.xx.fbcdn.net/...",
            "baglanti": "https://www.facebook.com/photo.php?fbid=...",
            "aciklama": "karpuz görseli olabilir"
        }
    ],
    "cekilis_tarihi": "2026-10-13 16:36:04"
}
```

Varsayılan sınırlar: en fazla 20 paylaşım, 100 arkadaş ve 50 fotoğraf (`_get_posts`, `_get_friends`, `_get_photos` parametreleriyle değiştirilebilir).

### Bilinen Sınırlamalar

-   **Paylaşım tarihi çekilemez:** Facebook tarihleri HTML içinde karıştırarak gösterir.
-   **Bazı paylaşımların bağlantısı yoktur:** Reels gibi paylaşımlarda `baglanti` alanı `"Bulunamadı"` olur.
-   **Sayaçlar sıraya göre okunur:** ifade, yorum ve paylaşım sayıları bu sırayla okunur; yorumu olmayan paylaşımlarda kayma olabilir.
-   **Türkçe arayüz gerekir:** Bölüm başlıkları ("Kişisel detaylar", "Arkadaşlar", "Fotoğraflar") Türkçe metinle aranır.
-   **Facebook arayüzü değişebilir:** Veriler gelmezse `debug` modunu açıp `ciktilar/debug` klasöründeki HTML dosyalarını inceleyin.

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

-   E-posta: trkglzgn_05@hotmail.com

---

Umarım bu kazıyıcı işinize yarar! Herhangi bir sorunla karşılaşırsanız, lütfen benimle iletişime geçmekten çekinmeyin.
