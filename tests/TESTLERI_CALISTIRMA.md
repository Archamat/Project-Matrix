# Testleri Çalıştırma Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. Gereksinimleri Yükle
```bash
pip install -r requirements.txt
```

veya sadece pytest:
```bash
pip install pytest pytest-cov
```

### 2. Tüm Testleri Çalıştır
```bash
pytest
```

### 3. Sadece Auth Testlerini Çalıştır
```bash
pytest tests/test_auth.py
```

## 📋 Detaylı Komutlar

### Verbose (Detaylı) Mod ile
Her testin adını ve sonucunu gösterir:
```bash
pytest tests/test_auth.py -v
```

### Belirli Bir Test Sınıfını Çalıştır
```bash
# Sadece login testleri
pytest tests/test_auth.py::TestHandleLogin -v

# Sadece register testleri
pytest tests/test_auth.py::TestHandleRegister -v

# Sadece logout testleri
pytest tests/test_auth.py::TestHandleLogout -v
```

### Belirli Bir Test Fonksiyonunu Çalıştır
```bash
pytest tests/test_auth.py::TestHandleLogin::test_handle_login_success -v
```

### Test Çıktısını Daha Ayrıntılı Göster
```bash
pytest tests/test_auth.py -v -s
```

### Sadece Başarısız Testleri Göster
```bash
pytest tests/test_auth.py -v --tb=short
```

## 📊 Coverage (Kod Kapsamı) Raporu

Hangi kodların test edildiğini görmek için:

### Terminal'de Kısa Rapor
```bash
pytest tests/test_auth.py --cov=app.auth.auth --cov-report=term
```

### HTML Rapor Oluştur
```bash
pytest tests/test_auth.py --cov=app.auth.auth --cov-report=html
```
Rapor `htmlcov/index.html` dosyasında oluşur. Tarayıcıda açabilirsiniz.

## 🔍 Test Çıktısı Örnekleri

### Başarılı Çıktı
```
============================= test session starts =============================
platform win32 -- Python 3.11.5, pytest-9.0.1
collected 16 items

tests/test_auth.py::TestHandleLogin::test_handle_login_success PASSED
tests/test_auth.py::TestHandleLogin::test_handle_login_invalid_password PASSED
...

============================= 16 passed in 6.19s ==============================
```

### Başarısız Test Örneği
Eğer bir test başarısız olursa, pytest hangi satırda hata olduğunu gösterir:
```
FAILED tests/test_auth.py::TestHandleLogin::test_handle_login_success
AssertionError: assert False is True
```

## 💡 İpuçları

### 1. Proje Root Dizininde Olun
Testleri çalıştırırken projenin ana dizininde olduğunuzdan emin olun:
```bash
cd D:\Work\Project-Matrix
pytest
```

### 2. Test Cache'i Temizleme
Eğer garip hatalar alırsanız:
```bash
pytest --cache-clear
```

### 3. Sadece Son Başarısız Testleri Çalıştır
```bash
pytest --lf  # last failed
```

### 4. Hızlı Mod (İlk Hatada Durdur)
```bash
pytest tests/test_auth.py -x
```

### 5. Paralel Çalıştırma (Hızlı Bilgisayarlar için)
```bash
pip install pytest-xdist
pytest tests/test_auth.py -n auto
```

## ❌ Yaygın Hatalar ve Çözümleri

### Import Hatası
**Hata:** `ModuleNotFoundError: No module named 'app'`

**Çözüm:** Projenin root dizininde olduğunuzdan emin olun:
```bash
cd D:\Work\Project-Matrix
pytest
```

### pytest Bulunamadı
**Hata:** `'pytest' is not recognized`

**Çözüm:** pytest'i yükleyin:
```bash
pip install pytest
```

### Mock Hatası
**Hata:** Mock çalışmıyor

**Çözüm:** `unittest.mock` Python 3.3+ ile gelir. Python versiyonunuzu kontrol edin:
```bash
python --version
```

## 📝 Örnek Test Çalıştırma Senaryoları

### Senaryo 1: Hızlı Kontrol
Sadece testlerin çalıştığını görmek istiyorsunuz:
```bash
pytest tests/test_auth.py -v
```

### Senaryo 2: Debug Modu
Bir test neden başarısız olduğunu anlamak istiyorsunuz:
```bash
pytest tests/test_auth.py::TestHandleLogin::test_handle_login_success -v -s
```

### Senaryo 3: Coverage Raporu
Kodunuzun ne kadarının test edildiğini görmek istiyorsunuz:
```bash
pytest tests/test_auth.py --cov=app.auth.auth --cov-report=html
# Sonra htmlcov/index.html dosyasını açın
```

### Senaryo 4: Belirli Bir Sorunu Test Etme
Sadece register işlemindeki eksik bilgi testlerini çalıştırmak:
```bash
pytest tests/test_auth.py::TestHandleRegister::test_handle_register_missing_username -v
pytest tests/test_auth.py::TestHandleRegister::test_handle_register_missing_password -v
pytest tests/test_auth.py::TestHandleRegister::test_handle_register_missing_email -v
```

## 🎯 Test Sonuçlarını Anlama

- ✅ **PASSED**: Test başarılı
- ❌ **FAILED**: Test başarısız (hata var)
- ⚠️ **ERROR**: Test çalıştırılamadı (syntax hatası vs.)
- ⏭️ **SKIPPED**: Test atlandı

Her bir test için ne kadar süre aldığı da gösterilir.

## 🔧 IDE'de Çalıştırma

### VS Code
1. Test dosyasını açın (`tests/test_auth.py`)
2. Üstteki "Run Test" butonuna tıklayın
3. Veya F5'e basıp test seçin

### PyCharm
1. Test dosyasını açın
2. Sağ tık → "Run 'pytest in test_auth.py'"
3. Veya yeşil oka tıklayın

---

**Not:** Testler mock kullandığı için veritabanı bağlantısı gerekmez. Testler bağımsız ve hızlı çalışır.

