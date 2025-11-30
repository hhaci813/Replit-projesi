"""Cloud Backup Sistemi - Otomatik bulut yedeklemesi"""
import json
import os
import shutil
import subprocess
from datetime import datetime

class CloudBackup:
    @staticmethod
    def yerel_yedekle():
        """Yerel yedekleme"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_klasor = f"backups/{timestamp}"
            os.makedirs(backup_klasor, exist_ok=True)
            
            # Ana dosyaları kopyala
            shutil.copy2('veriler.json', f"{backup_klasor}/veriler.json")
            shutil.copy2('portfoy_kayit.csv', f"{backup_klasor}/portfoy_kayit.csv")
            
            # Dosya listesi oluştur
            with open(f"{backup_klasor}/manifest.json", 'w') as f:
                json.dump({
                    "backup_tarihi": datetime.now().isoformat(),
                    "dosyalar": ["veriler.json", "portfoy_kayit.csv"]
                }, f)
            
            return f"✅ Yerel backup: {backup_klasor}"
        except Exception as e:
            return f"❌ Backup hatası: {e}"
    
    @staticmethod
    def github_sync():
        """GitHub'a senkronize et"""
        try:
            os.system("git add -A")
            os.system(f'git commit -m "Auto backup {datetime.now()}"')
            os.system("git push")
            return "✅ GitHub senkronizasyonu tamamlandı"
        except:
            return "⚠️ GitHub senkronizasyonu başarısız"
    
    @staticmethod
    def otomatik_backup():
        """Otomatik backup (her saat)"""
        print(CloudBackup.yerel_yedekle())
        print(CloudBackup.github_sync())

if __name__ == "__main__":
    CloudBackup.otomatik_backup()
