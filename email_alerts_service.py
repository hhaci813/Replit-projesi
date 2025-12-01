"""📧 Email Digest - Günlük özet rapor"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailAlertsService:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = None
        self.sender_password = None
    
    def set_credentials(self, email, password):
        """Gmail credentials ayarla"""
        self.sender_email = email
        self.sender_password = password
    
    def send_daily_digest(self, recipient_email, analysis_data):
        """Günlük özet rapor gönder"""
        try:
            if not self.sender_email or not self.sender_password:
                print("❌ Email credentials ayarlanmamış")
                return False
            
            # Rising/Falling assets
            rising = analysis_data.get('rising', [])[:5]
            falling = analysis_data.get('falling', [])[:5]
            
            # HTML body
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                    h1 {{ color: #00aa00; }}
                    .section {{ margin: 20px 0; border-bottom: 1px solid #ddd; padding-bottom: 15px; }}
                    .up {{ color: green; font-weight: bold; }}
                    .down {{ color: red; font-weight: bold; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊 AKILLI YATIRIM ASİSTANI - Günlük Özet</h1>
                    <p>Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                    
                    <div class="section">
                        <h2>📈 En Yükselenler</h2>
                        <table>
                            <tr><th>Sembol</th><th>Fiyat</th><th>Değişim</th></tr>
            """
            
            for asset in rising:
                html += f"<tr><td>{asset.get('symbol', 'N/A')}</td><td>₺{asset.get('price', 0):.0f}</td><td class='up'>+{asset.get('change', 0):.2f}%</td></tr>"
            
            html += """
                        </table>
                    </div>
                    
                    <div class="section">
                        <h2>📉 En Düşenler</h2>
                        <table>
                            <tr><th>Sembol</th><th>Fiyat</th><th>Değişim</th></tr>
            """
            
            for asset in falling:
                html += f"<tr><td>{asset.get('symbol', 'N/A')}</td><td>₺{asset.get('price', 0):.0f}</td><td class='down'>{asset.get('change', 0):.2f}%</td></tr>"
            
            html += """
                        </table>
                    </div>
                    
                    <div class="section">
                        <p>✅ Dashboard: <a href="http://localhost:5000/">http://localhost:5000/</a></p>
                        <p>📱 Telegram bot ile daha fazla bilgi alabilirsin</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Email gönder
            message = MIMEMultipart("alternative")
            message["Subject"] = "📊 Günlük Market Özeti"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            print(f"✅ Email gönderildi: {recipient_email}")
            return True
        
        except Exception as e:
            print(f"❌ Email gönderme hatası: {e}")
            return False
    
    def send_alert(self, recipient_email, alert_type, message):
        """Anlık alert gönder"""
        try:
            if not self.sender_email or not self.sender_password:
                return False
            
            email_msg = MIMEMultipart()
            email_msg["Subject"] = f"⚠️ {alert_type}"
            email_msg["From"] = self.sender_email
            email_msg["To"] = recipient_email
            
            email_msg.attach(MIMEText(message, "plain"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, email_msg.as_string())
            
            print(f"✅ Alert email gönderildi: {alert_type}")
            return True
        except Exception as e:
            print(f"❌ Alert email hatası: {e}")
            return False

if __name__ == "__main__":
    service = EmailAlertsService()
    print("📧 Email Alerts Service Hazır")
