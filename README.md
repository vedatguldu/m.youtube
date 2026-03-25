<h1 align="center">YouTube Masaüstü Oynatıcı (v1.0)</h1>

<p align="center">
  <b>YouTube videolarını aramak, canlı izlemek (streaming), yüksek kalitede indirmek ve hesaplarınızı yönetmek için tasarlanmış, WCAG 2.1 standartlarına uygun masaüstü uygulamasıdır.</b>
</p>

---

## 🌟 Öne Çıkan Özellikler

1. **Arama ve Keşfetme:**
   - Videoları hızlıca arayın, listeleyin.
   - Bağlam (sağ tık) menüsüyle anında oynatın veya bilgisayarınıza indirin.
2. **Erişilebilir Medya Oynatıcı:**
   - Hızlı ses değişimlerinde dalgalanmayı önleyen (200ms debounce) özel altyapı.
   - `%100` klavye kontrolü: `Space` (Başlat/Durdur), `Ok Tuşları` (Sarma/Ses), `F` (Tam Ekran), `M` (Sessiz).
   - Ekran okuyucular (NVDA, JAWS vb.) için her bir buton ve öğe özel olarak (aria-label mantığıyla) etiketlenmiştir.
3. **Akıllı İndirme Yöneticisi:**
   - Videoları arka planda (kuyruklu sistem) indirin, arayüz asla donmasın.
   - En iyi ses ve görüntüyü otomatik çekip `mkv` formatında birleştirir.
4. **Çalma Listeleri ve İzleme Geçmişi:**
   - İzlediğiniz her videonun kaydı tutulur (Yerel, sadece sizin bilgisayarınızda).
   - Sınırsız sayıda yerel çalma listesi oluşturabilir, videolarınızı kategorize edebilirsiniz.
5. **Google/YouTube Hesap Doğrulaması:**
   - Çerez (cookie) bulma işlemlerine gerek yok! Ayarlar kısmından tek tuşla **"Cihaz Onaylama Akışı (OAuth2)"** sayesinde güvenle YouTube hesabınıza bağlanın.
   - Bu sayede **YouTube Premium** veya abone olduğunuz **"Katıl" (Members-only)** videolarına da doğrudan erişebilirsiniz.
6. **Karanlık Tema (Dark Mode) ve Çoklu Dil:**
   - `İngilizce`, `Türkçe`, `İspanyolca` ve `Arapça` dil destekleri eklidir.
   - Sağ üstteki `🌙` ikonuna basarak anında Karanlık temaya geçiş yapın.

## 🛠 Kullanılan Teknolojiler

*   **Arayüz (GUI):** `PySide6` (Qt Framework'ün en modern Python sürümü).
*   **Ağ & Medya İndirme:** `yt-dlp` (Tamamen asenkron QThread mimarisi ile sisteme yük bindirmez).
*   **Oynatıcı Motoru:** Native `QMediaPlayer` ve `QAudioOutput`.

## 🚀 Kurulum ve Çalıştırma

Uygulamayı kendi bilgisayarınızda derleyip bir `.exe` (veya `.app`) haline getirmek oldukça kolaydır.

### 1. Gereksinimleri Yükleyin
Eğer kodu doğrudan çalıştırmak veya derlemek istiyorsanız sisteminizde Python 3.10+ kurulu olmalıdır.
```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Başlatın (Test İçin)
```bash
export PYTHONPATH=$(pwd)/src
python src/main.py
```

### 3. Paketleme / Derleme (Tek Dosya Haline Getirme)
Eğer dağıtıma hazır bir masaüstü uygulaması yaratmak isterseniz:
```bash
python build.py
```
*Not: İşlem bittiğinde `dist/` klasörü içinde **YouTubeDesktop** isimli tıklayıp çalıştırabileceğiniz uygulamanız hazır olacaktır.*

## ⚖️ Lisans ve Kullanım Koşulları (GPLv3)

**Telif Hakkı (C) 2026 Vedat Güldü**

Bu uygulama ve içerdiği tüm kaynak kodlar **GNU General Public License v3.0 (GPLv3)** lisansı ile korunmaktadır.

Bu lisans uyarınca:
*   Kodu dilediğiniz gibi kullanabilir, değiştirebilir ve geliştirebilirsiniz.
*   Ancak, bu kodu kullanarak geliştireceğiniz yeni projeleri de **kesinlikle aynı açık kaynak lisansı (GPLv3) ile ücretsiz olarak yayınlamak zorundasınız.**
*   Bu projenin kaynak kodlarını, yazarın (Vedat Güldü) açık ticari izni olmadan **kapalı kaynaklı (ticari/ücretli) bir ürün haline getiremezsiniz.**

Ticari kullanım, Pro sürüm hakları veya özel lisans anlaşmaları için lütfen **Vedat Güldü** ile iletişime geçin. Tam lisans metni için projedeki `LICENSE` dosyasına bakabilirsiniz.

---
*Faz 2'de (v2.0) "Birlikte İzle ve Sesli Sohbet (Watch Party)" özellikleri planlanmaktadır.*
