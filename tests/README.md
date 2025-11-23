# Test Dokümantasyonu

## Test Dosyası: `test_auth.py`

Bu dosya `app/auth/auth.py` modülündeki üç fonksiyonu test eder:
- `handle_login()` - Kullanıcı giriş işlemi
- `handle_register()` - Kullanıcı kayıt işlemi
- `handle_logout()` - Kullanıcı çıkış işlemi

## Test Stratejisi

### Mocking (Sahte Nesneler)
Testlerde **Mock** kullanıyoruz çünkü:
1. **Veritabanı bağımlılığını kaldırır** - Gerçek veritabanına bağlanmadan test edebiliriz
2. **Hızlı çalışır** - Veritabanı işlemleri yavaş olabilir
3. **İzole test** - Testler birbirini etkilemez
4. **Kontrollü test** - İstediğimiz sonuçları döndürebiliriz

### Test Edilen Senaryolar

#### 1. `handle_login()` Testleri
- ✅ **Başarılı giriş**: Kullanıcı adı ve şifre doğru
- ❌ **Hatalı şifre**: Şifre yanlış
- ❌ **Kullanıcı yok**: Kullanıcı bulunamadı
- ❌ **Eksik kullanıcı adı**: Username girilmemiş
- ❌ **Eksik şifre**: Password girilmemiş
- ❌ **Boş kullanıcı adı**: Username boş string
- ❌ **login_user hatası**: Flask-Login hata verirse

#### 2. `handle_register()` Testleri
- ✅ **Başarılı kayıt**: Yeni kullanıcı oluşturuldu
- ❌ **Kullanıcı adı mevcut**: Username zaten kullanılıyor
- ❌ **Eksik bilgiler**: Username, password veya email eksik
- ❌ **Oluşturma hatası**: create_user None döndü
- ❌ **Veritabanı hatası**: Exception fırlatıldı

#### 3. `handle_logout()` Testleri
- ✅ **Başarılı çıkış**: Logout başarılı
- ❌ **Çıkış hatası**: logout_user exception fırlattı

## Testleri Çalıştırma

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Tüm testleri çalıştır
```bash
pytest
```

### Sadece auth testlerini çalıştır
```bash
pytest tests/test_auth.py
```

### Detaylı çıktı ile
```bash
pytest tests/test_auth.py -v
```

### Belirli bir test sınıfını çalıştır
```bash
pytest tests/test_auth.py::TestHandleLogin -v
```

### Belirli bir testi çalıştır
```bash
pytest tests/test_auth.py::TestHandleLogin::test_handle_login_success -v
```

### Coverage (Kod kapsamı) raporu
```bash
pytest tests/test_auth.py --cov=app.auth.auth --cov-report=html
```

## Test Yapısı

### Test Sınıfları
Her fonksiyon için ayrı bir test sınıfı oluşturduk:
- `TestHandleLogin`
- `TestHandleRegister`
- `TestHandleLogout`

### Mock Kullanımı
```python
@patch('app.auth.auth.login_user')  # Flask-Login fonksiyonunu mock'la
@patch('app.auth.auth.AuthDatabaseManager')  # Database manager'ı mock'la
def test_handle_login_success(self, mock_auth_db_manager, mock_login_user):
    # Mock'ları ayarla
    mock_user = Mock()
    mock_user.check_password.return_value = True
    mock_auth_db_manager.get_user_by_username.return_value = mock_user
    
    # Testi çalıştır
    result = handle_login({'username': 'test', 'password': 'pass'})
    
    # Sonuçları kontrol et
    assert result is True
```

### Assert Kullanımı
- `assert result is True` - Sonucun True olduğunu kontrol eder
- `assert result == {...}` - Dictionary karşılaştırması
- `pytest.raises()` - Hata fırlatılıp fırlatılmadığını kontrol eder

## Önemli Noktalar

1. **Mock Decorator Sırası**: `@patch` decorator'ları alt alta yazıldığında, en üstteki en sağdaki parametreye karşılık gelir.

2. **Patch Yolu**: `'app.auth.auth.AuthDatabaseManager'` şeklinde, fonksiyonun import edildiği modüle göre yazılır.

3. **Test İzolasyonu**: Her test bağımsız çalışır, bir test diğerini etkilemez.

4. **Edge Cases**: Eksik bilgiler, None değerler, boş stringler gibi durumlar test edilir.

## Yeni Test Ekleme

Yeni bir test eklemek için:

```python
def test_yeni_senaryo(self, mock_dependency):
    """
    Senaryo açıklaması
    - Ne test ediliyor
    - Ne bekleniyor
    """
    # Arrange: Hazırlık
    mock_dependency.return_value = something
    
    # Act: Testi çalıştır
    result = function_to_test(data)
    
    # Assert: Kontrol et
    assert result == expected_value
```

## Sorun Giderme

### Import hatası alıyorsanız:
```bash
# Proje root dizininde olduğunuzdan emin olun
cd D:\Work\Project-Matrix
pytest
```

### ModuleNotFoundError:
- `__init__.py` dosyalarının olduğundan emin olun
- Python path'inin doğru olduğundan emin olun

