# YouTube Masaüstü - Erişilebilir Oynatıcı (v1.0)
*YouTube Desktop - Accessible Player*

YouTube videolarını aramak, canlı akış (streaming) olarak izlemek, çalma listeleri oluşturmak ve yüksek kalitede indirebilmek için tasarlanmış, **WCAG 2.1 AA/AAA standartlarında tam erişilebilir** masaüstü uygulamasıdır.

## 🌟 Özellikler (Features)

1. **Arama ve Keşfetme:**
   - Videoları hızlıca arayın, ızgara (grid) formatında görüntüleyin.
   - Sağ tıklayarak oynatın veya doğrudan indirin.
2. **Erişilebilir Medya Oynatıcı:**
   - 200ms gecikme önleyici (debounce) sistemli ses kontrolü.
   - Tamamen klavye kontrollü (`Space`, `F`, `M`, ok tuşları).
   - NVDA ve JAWS ekran okuyucular için `%100` etiketlendirilmiş altyapı.
3. **İndirme Yöneticisi:**
   - Arka planda asenkron çoklu indirme kuyruğu.
   - En iyi kalite (1080p, 4K vb.) formatların `mkv` olarak sorunsuz birleşimi.
4. **Çalma Listeleri ve İzleme Geçmişi:**
   - Kendi yerel çalma listelerinizi oluşturun ve yönetin.
   - İzlediğiniz veya indirdiğiniz tüm videoları anında tekrar oynatın.
5. **Google/YouTube Hesap Doğrulaması:**
   - Karmaşık çerez (cookie) bulma işlemlerine gerek kalmadan, **OAuth2 Device Flow** (Cihaz Onaylama Akışı) sayesinde tek tıklamayla güvenli giriş.
   - Bu sayede YouTube Premium ve Katıl (Members-only) videolarına tam erişim.
6. **Tema ve Dil:**
   - `İngilizce`, `Türkçe`, `İspanyolca` ve `Arapça` tam destek (Menüden ve Ayarlardan değiştirilebilir).
   - `Karanlık` (Dark) ve `Aydınlık` (Light) tema arasında tek tuşla (🌙) anında geçiş.

## 🛠 Mimari & Teknoloji (Tech Stack)

*   **Arayüz:** `PySide6` (Qt for Python)
*   **Ağ & Veri Çekme:** `yt-dlp` (Asenkron QThread mimarisi ile donmaları engeller)
*   **Multimedya:** `QMediaPlayer` ve `QAudioOutput` (720p birleşik format destekli optimize akış)
*   **Paketleme:** `PyInstaller` (Tam bağımsız işletim sistemi dosyaları için)

## ⌨️ Klavye Kısayolları (Shortcuts)

| Kısayol | İşlev |
| :--- | :--- |
| `Alt+1` | Keşfet sekmesine git |
| `Alt+2` | İndirmeler sekmesine git |
| `Alt+3` | Çalma Listeleri sekmesine git |
| `Alt+4` | Geçmiş sekmesine git |
| `Ctrl+F` | Arama çubuğuna odaklan |
| `Ctrl+O` | İndirme klasörünü aç |
| `Ctrl+Q` | Uygulamadan çık |
| `Space` | Oynat / Duraklat (Oynatıcı aktifken) |
| `F` | Tam ekrana geç / çık |
| `M` | Sesi kapat / aç (Mute) |

## 🚀 Kurulum ve Çalıştırma (Installation & Build)

Bu uygulama herhangi bir Python bilgisi veya kurulumu gerektirmeden çalıştırılabilir olacak şekilde tasarlanmıştır.

### Geliştirici Ortamı (Developer Setup)
Eğer kodu doğrudan çalıştırmak istiyorsanız:
```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
export PYTHONPATH=$(pwd)/src
python src/main.py
```

### Derleme (Building .exe / .app)
Kullanıcılara dağıtmak üzere tek bir çalıştırılabilir dosya üretmek için:
```bash
python build.py
```
Bu işlem sonunda `dist/` klasörü içerisinde `YouTubeDesktop` isimli çalıştırılabilir native uygulamanız oluşacaktır.

## 🤝 Faz 2 (Gelecek Özellikler)
İlerleyen güncellemelerde "Birlikte İzle ve Sesli Sohbet (Watch Party & Voice Chat)" özellikleri eklenecektir.
