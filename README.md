# 🏨 Otel Rezervasyon Sistemi

Modern ve kullanıcı dostu bir otel rezervasyon sistemi. Flask framework'ü kullanılarak geliştirilmiş, güvenli ve ölçeklenebilir bir web uygulaması.

## 🌟 Özellikler

### 👥 Kullanıcı Yönetimi
- Kullanıcı kaydı ve girişi
- Profil yönetimi
- Rezervasyon geçmişi görüntüleme
- Değerlendirme ve yorum yapabilme

### 🛏️ Oda Yönetimi
- Farklı oda tipleri (Standart, Deluxe, Suite)
- Detaylı oda bilgileri ve fotoğraflar
- Oda özellikleri (balkon, deniz manzarası vb.)
- Gerçek zamanlı müsaitlik kontrolü

### 📅 Rezervasyon Sistemi
- Online rezervasyon oluşturma
- Tarih bazlı müsaitlik kontrolü
- Özel isteklerin belirtilebilmesi
- Otomatik fiyat hesaplama

### 💳 Ödeme Sistemi
- Güvenli ödeme işlemleri
- Farklı ödeme yöntemleri (kredi kartı, banka transferi, nakit)
- Rezervasyon iptal ve iade yönetimi

### 📱 Bildirim Sistemi
- Rezervasyon onayı bildirimleri
- Ödeme durumu güncellemeleri
- Sistem bildirimleri

### 👨‍💼 Admin Paneli
- Rezervasyon yönetimi
- Oda düzenleme ve ekleme
- Kullanıcı yönetimi
- Bakım kayıtları
- Detaylı raporlar ve istatistikler

## 🛠️ Teknolojiler

- **Backend:** Python, Flask
- **Veritabanı:** SQLAlchemy ORM
- **Frontend:** HTML, CSS, JavaScript
- **Güvenlik:** Flask-Login, Werkzeug
- **Email:** Flask-Mail
- **Veritabanı Migrasyonları:** Flask-Migrate

## 📦 Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/tfyaliniz/otel-rezervasyon-sistemi.git
cd otel-rezervasyon-sistemi
```

2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv venv
# Windows için
venv\Scripts\activate
# Linux/Mac için
source venv/bin/activate
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Uygulamayı başlatın:
```bash
flask run
```

## 🔧 Konfigürasyon

`config.py` dosyasında aşağıdaki ayarları yapılandırın:

- Veritabanı bağlantı bilgileri
- Email sunucu ayarları
- Uygulama gizli anahtarı
- Dosya yükleme dizini

> **UYARI:** Gizli bilgilerinizi (şifre, API anahtarı, e-posta, reCAPTCHA anahtarları vb.) doğrudan dosyaya yazmayın. Bunları ortam değişkenleriyle veya güvenli bir şekilde ekleyin. `config.py` dosyasındaki örnek placeholder'ları kendi bilgilerinizle değiştirin.

## 📝 Kullanım

1. `/register` endpoint'i üzerinden yeni kullanıcı kaydı oluşturun
2. `/login` endpoint'i üzerinden giriş yapın
3. Ana sayfadan müsait odaları görüntüleyin
4. Rezervasyon oluşturun ve ödeme yapın

## 👥 Katkıda Bulunma

1. Bu repoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: Açıklama'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

- Proje Sahibi: Taha Furkan YALINIZ
- GitHub: [https://github.com/tfyaliniz](https://github.com/tfyaliniz)
- LinkedIn: [https://www.linkedin.com/in/tfyaliniz/](https://www.linkedin.com/in/tfyaliniz/)

## 🙏 Teşekkürler

Bu projeye katkıda bulunan herkese teşekkürler! 