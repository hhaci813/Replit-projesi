"""Güvenlik Sistemi - Password Hashing + Encryption"""
import bcrypt
import json
import os
from cryptography.fernet import Fernet
import base64

class SecurityManager:
    def __init__(self):
        self.key_file = ".security_key"
        self.cipher = self.load_or_create_key()
    
    def load_or_create_key(self):
        """Encryption key yükle veya oluştur"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        return Fernet(key)
    
    def hash_password(self, password):
        """Şifreyi hash'le"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def verify_password(self, password, hashed):
        """Şifre doğrula"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    def encrypt_api_key(self, api_key):
        """API key'i şifrele"""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key):
        """API key'i çöz"""
        try:
            return self.cipher.decrypt(encrypted_key.encode()).decode()
        except:
            return None
    
    def encrypt_file(self, file_path):
        """Dosyayı şifrele"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.cipher.encrypt(data)
        with open(f"{file_path}.encrypted", 'wb') as f:
            f.write(encrypted)
        return True
    
    def decrypt_file(self, encrypted_file):
        """Dosyayı çöz"""
        with open(encrypted_file, 'rb') as f:
            encrypted = f.read()
        
        data = self.cipher.decrypt(encrypted)
        with open(encrypted_file.replace('.encrypted', ''), 'wb') as f:
            f.write(data)
        return True

if __name__ == "__main__":
    security = SecurityManager()
    print("✅ Security Manager Aktif")
