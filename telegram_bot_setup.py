"""Telegram Bot Kurulum - Chat ID bulma"""
import os
import requests

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def get_bot_info():
    """Bot bilgilerini al"""
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return None
    
    print(f"🔍 Testing token: {TOKEN[:15]}...{TOKEN[-5:]}")
    
    try:
        # Test getMe
        resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=10)
        print(f"📡 getMe Response: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Bot Found: @{data['result']['username']}")
            print(f"   Bot ID: {data['result']['id']}")
            return data['result']
        else:
            print(f"❌ Error: {resp.text}")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def get_updates():
    """Son mesajları al ve chat_id bul"""
    if not TOKEN:
        return
    
    try:
        resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            updates = data.get('result', [])
            
            if updates:
                print(f"\n📬 Son {len(updates)} mesaj:")
                for u in updates[-5:]:  # Son 5 mesaj
                    if 'message' in u:
                        msg = u['message']
                        chat_id = msg['chat']['id']
                        user = msg.get('from', {}).get('first_name', 'Unknown')
                        text = msg.get('text', '')[:50]
                        print(f"   Chat ID: {chat_id} | User: {user} | Text: {text}")
            else:
                print("\n⚠️ Henüz mesaj yok. Bot'a bir mesaj gönderin!")
        else:
            print(f"❌ getUpdates error: {resp.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TELEGRAM BOT SETUP")
    print("=" * 60)
    
    bot = get_bot_info()
    
    if bot:
        print("\n✅ Bot çalışıyor!")
        get_updates()
        print("\n💡 Chat ID'nizi bulmak için:")
        print("   1. Telegram'da bot'a mesaj gönderin")
        print("   2. Bu scripti tekrar çalıştırın")
    else:
        print("\n❌ Bot bağlantısı başarısız!")
        print("   Token'ın doğru olduğundan emin olun")

