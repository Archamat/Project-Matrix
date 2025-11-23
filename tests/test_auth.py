"""
Test dosyası: app/auth/auth.py için unit testler

Bu test dosyası auth.py içindeki üç ana fonksiyonu test eder:
1. handle_login - Giriş işlemi
2. handle_register - Kayıt işlemi  
3. handle_logout - Çıkış işlemi

Test Stratejisi:
- Mock kullanarak AuthDatabaseManager ve flask_login'i izole ediyoruz
- Her fonksiyon için hem başarılı hem de hata durumlarını test ediyoruz
- Edge case'leri (eksik bilgiler, None değerler vs.) kontrol ediyoruz
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.auth.auth import handle_login, handle_register, handle_logout


class TestHandleLogin:
    """handle_login fonksiyonu için testler"""
    
    @patch('app.auth.auth.login_user')
    @patch('app.auth.auth.AuthDatabaseManager')
    def test_handle_login_success(self, mock_auth_db_manager, mock_login_user):
        """
        Başarılı giriş senaryosu
        - Kullanıcı adı ve şifre doğru
        - login_user çağrılmalı
        - True dönmeli
        """
        # Mock kullanıcı oluştur
        mock_user = Mock()
        mock_user.check_password.return_value = True
        
        # AuthDatabaseManager'in döndüreceği kullanıcıyı ayarla
        mock_auth_db_manager.get_user_by_username.return_value = mock_user
        
        # Test data
        data = {'username': 'testuser', 'password': 'testpass123'}
        
        # Fonksiyonu çağır
        result = handle_login(data)
        
        # Kontroller
        assert result is True
        mock_auth_db_manager.get_user_by_username.assert_called_once_with('testuser')
        mock_user.check_password.assert_called_once_with('testpass123')
        mock_login_user.assert_called_once_with(mock_user)
    
    @patch('app.auth.auth.AuthDatabaseManager')
    def test_handle_login_invalid_password(self, mock_auth_db_manager):
        """
        Hatalı şifre senaryosu
        - Kullanıcı var ama şifre yanlış
        - ValueError fırlatmalı
        """
        # Mock kullanıcı oluştur (şifre yanlış)
        mock_user = Mock()
        mock_user.check_password.return_value = False
        
        mock_auth_db_manager.get_user_by_username.return_value = mock_user
        
        data = {'username': 'testuser', 'password': 'wrongpass'}
        
        # ValueError bekliyoruz
        with pytest.raises(ValueError, match='Invalid username or password'):
            handle_login(data)
    
    @patch('app.auth.auth.AuthDatabaseManager')
    def test_handle_login_user_not_found(self, mock_auth_db_manager):
        """
        Kullanıcı bulunamadı senaryosu
        - Kullanıcı veritabanında yok
        - ValueError fırlatmalı
        """
        # Kullanıcı None dönüyor
        mock_auth_db_manager.get_user_by_username.return_value = None
        
        data = {'username': 'nonexistent', 'password': 'anypass'}
        
        with pytest.raises(ValueError, match='Invalid username or password'):
            handle_login(data)
    
    def test_handle_login_missing_username(self):
        """
        Eksik kullanıcı adı senaryosu
        - Username yok
        - ValueError fırlatmalı
        """
        data = {'password': 'testpass123'}
        
        with pytest.raises(ValueError, match='Username and password are required'):
            handle_login(data)
    
    def test_handle_login_missing_password(self):
        """
        Eksik şifre senaryosu
        - Password yok
        - ValueError fırlatmalı
        """
        data = {'username': 'testuser'}
        
        with pytest.raises(ValueError, match='Username and password are required'):
            handle_login(data)
    
    def test_handle_login_empty_username(self):
        """
        Boş kullanıcı adı senaryosu
        - Username boş string
        - ValueError fırlatmalı
        """
        data = {'username': '', 'password': 'testpass123'}
        
        with pytest.raises(ValueError, match='Username and password are required'):
            handle_login(data)
    
    @patch('app.auth.auth.login_user')
    @patch('app.auth.auth.AuthDatabaseManager')
    def test_handle_login_login_user_exception(self, mock_auth_db_manager, mock_login_user):
        """
        login_user hata fırlatırsa
        - login_user exception fırlatırsa
        - ValueError fırlatmalı ve hata mesajını içermeli
        """
        mock_user = Mock()
        mock_user.check_password.return_value = True
        mock_auth_db_manager.get_user_by_username.return_value = mock_user
        
        # login_user hata fırlatsın
        mock_login_user.side_effect = Exception("Database connection failed")
        
        data = {'username': 'testuser', 'password': 'testpass123'}
        
        with pytest.raises(ValueError, match='Login failed'):
            handle_login(data)


class TestHandleRegister:
    """handle_register fonksiyonu için testler"""
    
    @patch('app.auth.auth.AuthDatabaseManager')
    def test_handle_register_success(self, mock_auth_db_manager):
        """
        Başarılı kayıt senaryosu
        - Tüm bilgiler doğru
        - Kullanıcı oluşturulmalı
        - Hata fırlatmamalı
        """
        # Yeni kullanıcı oluşturulacak (daha önce yok)
        mock_auth_db_manager.get_user_by_username.return_value = None
        
        # Oluşturulan kullanıcıyı mock'la
        mock_user = Mock()
        mock_auth_db_manager.create_user.return_value = mock_user
        
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        }
        
        # Fonksiyon hata fırlatmamalı
        handle_register(data)
        
        # Kontroller
        mock_auth_db_manager.get_user_by_username.assert_called_once_with('newuser')
        mock_auth_db_manager.create_user.assert_called_once_with(
            'newuser', 'newuser@example.com', 'newpass123'
        )
    
    @patch('app.auth.auth.AuthDatabaseManager')
    def test_handle_register_username_already_exists(self, mock_auth_db_manager):
        """
        Kullanıcı adı zaten var senaryosu
        - Username zaten kullanılıyor
        - ValueError fırlatmalı
        """
        # Kullanıcı zaten var
        existing_user = Mock()
        mock_auth_db_manager.get_user_by_username.return_value = existing_user
        
        data = {
            'username': 'existinguser',
            'password': 'pass123',
            'email': 'user@example.com'
        }
        
        with pytest.raises(ValueError, match='Username already exists'):
            handle_register(data)
        
        # create_user çağrılmamalı
        mock_auth_db_manager.create_user.assert_not_called()
    
    def test_handle_register_missing_username(self):
        """
        Eksik kullanıcı adı senaryosu
        - Username yok
        - ValueError fırlatmalı
        """
        data = {
            'password': 'pass123',
            'email': 'user@example.com'
        }
        
        with pytest.raises(ValueError, match='Username, password, and email are required'):
            handle_register(data)
    
    def test_handle_register_missing_password(self):
        """
        Eksik şifre senaryosu
        - Password yok
        - ValueError fırlatmalı
        """
        data = {
            'username': 'testuser',
            'email': 'user@example.com'
        }
        
        with pytest.raises(ValueError, match='Username, password, and email are required'):
            handle_register(data)
    
    def test_handle_register_missing_email(self):
        """
        Eksik email senaryosu
        - Email yok
        - ValueError fırlatmalı
        """
        data = {
            'username': 'testuser',
            'password': 'pass123'
        }
        
        with pytest.raises(ValueError, match='Username, password, and email are required'):
            handle_register(data)
    
    @patch('app.auth.auth.AuthDatabaseManager')
    def test_handle_register_create_user_returns_none(self, mock_auth_db_manager):
        """
        create_user None döndüğünde
        - Kullanıcı oluşturma başarısız olursa
        - ValueError fırlatmalı
        """
        mock_auth_db_manager.get_user_by_username.return_value = None
        mock_auth_db_manager.create_user.return_value = None
        
        data = {
            'username': 'testuser',
            'password': 'pass123',
            'email': 'user@example.com'
        }
        
        with pytest.raises(ValueError, match='An error occurred during registration'):
            handle_register(data)
    
    @patch('app.auth.auth.AuthDatabaseManager')
    def test_handle_register_create_user_exception(self, mock_auth_db_manager):
        """
        create_user exception fırlatırsa
        - Veritabanı hatası gibi durumlar
        - ValueError fırlatmalı ve hata mesajını içermeli
        """
        mock_auth_db_manager.get_user_by_username.return_value = None
        mock_auth_db_manager.create_user.side_effect = Exception("Database error")
        
        data = {
            'username': 'testuser',
            'password': 'pass123',
            'email': 'user@example.com'
        }
        
        with pytest.raises(ValueError, match='Registration failed'):
            handle_register(data)


class TestHandleLogout:
    """handle_logout fonksiyonu için testler"""
    
    @patch('app.auth.auth.logout_user')
    def test_handle_logout_success(self, mock_logout_user):
        """
        Başarılı çıkış senaryosu
        - logout_user çağrılmalı
        - Doğru response dönmeli
        """
        result = handle_logout()
        
        # Kontroller
        mock_logout_user.assert_called_once()
        assert result == {'success': True, 'message': 'Logged out successfully'}
    
    @patch('app.auth.auth.logout_user')
    def test_handle_logout_exception(self, mock_logout_user):
        """
        logout_user exception fırlatırsa
        - Logout sırasında hata olursa
        - ValueError fırlatmalı ve hata mesajını içermeli
        """
        mock_logout_user.side_effect = Exception("Session error")
        
        with pytest.raises(ValueError, match='Logout failed'):
            handle_logout()

