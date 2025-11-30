"""Chart Generator - Telegram'a veri-rich grafik gönder"""
import matplotlib.pyplot as plt
import yfinance as yf
from io import BytesIO
import base64

class ChartGenerator:
    @staticmethod
    def generate_analysis_chart(symbol, period="7d"):
        """7 günlük teknik analiz grafiği"""
        try:
            # Veri çek
            data = yf.download(symbol, period=period, progress=False)
            if data is None or data.empty:
                return None
            
            # Grafik oluştur
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), dpi=100)
            
            # Fiyat + MA
            ax1.plot(data.index, data['Close'], label='Fiyat', linewidth=2, color='blue')
            ax1.plot(data.index, data['Close'].rolling(7).mean(), label='MA7', linestyle='--', color='green')
            ax1.plot(data.index, data['Close'].rolling(20).mean(), label='MA20', linestyle='--', color='red')
            ax1.set_title(f'{symbol} Teknik Analiz - 7 Gün', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Fiyat ($)', fontsize=10)
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            
            # Volume
            ax2.bar(data.index, data['Volume'], color='gray', alpha=0.5)
            ax2.set_ylabel('Volume', fontsize=10)
            ax2.set_xlabel('Tarih', fontsize=10)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # BytesIO olarak kaydet
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except:
            return None
    
    @staticmethod
    def generate_portfolio_chart(assets_data):
        """Portföy dağılımı grafik"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            symbols = [a['symbol'] for a in assets_data]
            values = [a['value'] for a in assets_data]
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
            ax.pie(values, labels=symbols, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('Portföy Dağılımı', fontsize=14, fontweight='bold')
            
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
        except:
            return None
