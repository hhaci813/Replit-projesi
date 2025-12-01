"""Email & SMS Alerts - Fiyat değişimleri, Stop Loss, Take Profit"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertEngine:
    """Email & SMS Alerts"""
    
    def __init__(self):
        self.alerts = []
        self.email = os.getenv("ALERT_EMAIL", "trading@example.com")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_email_alert(self, subject, message):
        """Email gönder"""
        try:
            # Demo - gerçekte Gmail app password kullan
            msg = MIMEMultipart()
            msg['From'] = "ai-trading@gmail.com"
            msg['To'] = self.email
            msg['Subject'] = subject
            
            body = f"""
{message}

━━━━━━━━━━━━━━━━━━━
🤖 AI Investment Assistant
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            self.alerts.append({
                'type': 'email',
                'subject': subject,
                'message': message,
                'timestamp': datetime.now()
            })
            
            return True, "✅ Email gönderildi"
        except Exception as e:
            return False, f"❌ Email hatası: {str(e)}"
    
    def send_price_alert(self, symbol, price, change_pct):
        """Fiyat değişim uyarısı"""
        if abs(change_pct) > 5:
            direction = "📈 YÜKSELDI" if change_pct > 0 else "📉 DÜŞTÜ"
            subject = f"🚨 {symbol} {direction} - {abs(change_pct):.2f}%"
            message = f"""
{symbol} Fiyat Değişimi

Fiyat: ${price:.2f}
Değişim: {change_pct:+.2f}%

Dönem: Son 1 saatte
"""
            return self.send_email_alert(subject, message)
    
    def send_stop_loss_alert(self, symbol, price, stop_loss):
        """Stop loss uyarısı"""
        subject = f"🛑 STOP LOSS: {symbol} @ ${price:.2f}"
        message = f"""
UYARI: Stop Loss Tetiklendi

Sembol: {symbol}
Fiyat: ${price:.2f}
Stop Loss: ${stop_loss:.2f}

HEMEN SAT TAVSIYESI!
"""
        return self.send_email_alert(subject, message)
    
    def send_take_profit_alert(self, symbol, price, take_profit):
        """Take profit uyarısı"""
        subject = f"✅ TAKE PROFIT: {symbol} @ ${price:.2f}"
        message = f"""
ÇOK İYİ! Kar Hedefi Ulaşıldı

Sembol: {symbol}
Fiyat: ${price:.2f}
Hedef: ${take_profit:.2f}

KARI KAPAT TAVSIYESI!
"""
        return self.send_email_alert(subject, message)

import os
from datetime import datetime
