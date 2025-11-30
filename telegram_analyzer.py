"""Telegram'a Analiz Gönder"""
from telegram_service import TelegramService
from symbol_analyzer import SymbolAnalyzer

class TelegramAnalyzer:
    def __init__(self):
        self.telegram = TelegramService()
        self.analyzer = SymbolAnalyzer()
    
    def send_analysis(self, symbol):
        """Analizi Telegram'a gönder"""
        if symbol == "XRPTRY":
            result = self.analyzer.xrptry_manual_analysis()
            
            # Format message
            signal_emoji = result['signal'].split()[0]
            message = f"""
🔍 <b>XRPTRY ANALİZİ</b>

{result['signal']} <b>Sinyal</b>

💰 <b>Fiyat Seviyeleri:</b>
   • Mevcut: ₺{result['current_price']}
   • Support: ₺{result['support']}
   • Resistance: ₺{result['resistance']}
   • Hedef: ₺{result['target']}
   
🛑 <b>Risk Yönetimi:</b>
   • Stop Loss: ₺{result['stop_loss']}
   • Risk/Reward: {result['risk_reward']}x

📊 <b>Nedenler:</b>
"""
            for reason in result['reasons']:
                message += f"   ✓ {reason}\n"
            
            message += f"""
⏰ Analiz Saati: {self.get_current_time()}
"""
        else:
            result = self.analyzer.generate_signal(symbol)
            
            if result['signal'] == "?":
                message = f"❌ {symbol} analiz edilemedi: {result.get('reason', 'Bilinmeyen hata')}"
            else:
                message = f"""
🔍 <b>{symbol} ANALİZİ</b>

{result['signal']} <b>Sinyal</b>

📊 <b>Teknik Göstergeler:</b>
   • Fiyat: ${result['price']:.2f}
   • RSI: {result['rsi']:.1f}
   • MA20: ${result['ma20']:.2f}
   • MA50: ${result['ma50']:.2f}

📈 <b>Nedenler:</b>
"""
                for reason in result.get('reasons', []):
                    message += f"   ✓ {reason}\n"
        
        # Telegram'a gönder
        ok, msg = self.telegram.send_message(message)
        return ok, msg
    
    def get_current_time(self):
        """Mevcut saati getir"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y %H:%M")

if __name__ == "__main__":
    ta = TelegramAnalyzer()
    ok, msg = ta.send_analysis("XRPTRY")
    print(f"✅ Telegram: {ok} - {msg}")
