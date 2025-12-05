"""🤖 Telegram Bot Runner - Arka planda çalışır"""
import subprocess
import sys

def run_telegram_bot():
    """Telegram bot'u çalıştır"""
    print("🤖 Telegram Bot başlatılıyor...")
    
    try:
        import telebot
        print("✅ telebot yüklü")
    except:
        print("⚠️ telebot yükleniyor...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI"], check=False)
    
    try:
        # Run telegram command handler
        import telegram_btc_command
        handler = telegram_btc_command.BTCCommandHandler()
        
        # Test
        print("Testing /btc command...")
        report = handler.generate_report()
        print("✅ Bot ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_telegram_bot()

