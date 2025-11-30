"""Telegram Setup - Token ile yapılandır"""
import os
import requests

# Kullanıcı token'ı
USER_TOKEN = "8268294938:AAGCvDDNHhb5-pKFQYPJrZIJTxMVmu79oYo"
CHAT_ID = 8391537149

def setup_telegram():
    """Telegram setup yap"""
    # OS env'e set et
    os.environ['TELEGRAM_BOT_TOKEN'] = USER_TOKEN
    
    # Test et
    url = f"https://api.telegram.org/bot{USER_TOKEN}/getMe"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            bot_info = resp.json()['result']
            return True, f"✅ Bot: {bot_info.get('username', 'Unknown')}"
        else:
            return False, f"❌ Token error: {resp.status_code}"
    except Exception as e:
        return False, f"❌ Error: {e}"

def send_test_message():
    """Test mesaj gönder"""
    url = f"https://api.telegram.org/bot{USER_TOKEN}/sendMessage"
    message = "✅ AKILLI YATIRIM ASİSTANI - TEST MESAJ\n\n🚀 Sistem hazır ve çalışıyor!"
    data = {"chat_id": CHAT_ID, "text": message}
    
    try:
        resp = requests.post(url, json=data, timeout=5)
        return resp.status_code == 200, resp.json()
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("🔧 TELEGRAM SETUP")
    ok, msg = setup_telegram()
    print(f"  {msg}")
    
    if ok:
        print("\n📤 Test mesaj gönderiliyor...")
        ok, msg = send_test_message()
        print(f"  {'✅ Gönderildi!' if ok else f'❌ {msg}'}")
