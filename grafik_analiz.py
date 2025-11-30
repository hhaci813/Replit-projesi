"""Grafik Analizi - Technical Indicators & Candlestick"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class GrafikAnaliz:
    def __init__(self):
        self.fig_count = 0
    
    def bollinger_bands_grafik(self, symbol, period="3mo"):
        """Bollinger Bands grafiği"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            if data.empty:
                return "❌ Veri alınamadı"
            
            # Bollinger Bands hesapla
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['STD'] = data['Close'].rolling(window=20).std()
            data['Upper'] = data['MA20'] + (data['STD'] * 2)
            data['Lower'] = data['MA20'] - (data['STD'] * 2)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            ax.plot(data.index, data['Close'], label=symbol, color='black', linewidth=2)
            ax.plot(data.index, data['MA20'], label='MA(20)', color='blue', linewidth=1)
            ax.fill_between(data.index, data['Upper'], data['Lower'], alpha=0.2, color='gray', label='Bollinger Bands')
            
            ax.set_title(f'{symbol} - Bollinger Bands', fontsize=14, fontweight='bold')
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Fiyat ($)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            dosya = f'bollinger_bands_{symbol}.png'
            plt.savefig(dosya, dpi=100)
            plt.close()
            
            return f"✅ Bollinger Bands grafiği: {dosya}"
        except Exception as e:
            return f"❌ Hata: {str(e)}"
    
    def macd_grafik(self, symbol, period="3mo"):
        """MACD grafiği"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            if data.empty:
                return "❌ Veri alınamadı"
            
            # MACD hesapla
            exp1 = data['Close'].ewm(span=12).mean()
            exp2 = data['Close'].ewm(span=26).mean()
            data['MACD'] = exp1 - exp2
            data['Signal'] = data['MACD'].ewm(span=9).mean()
            data['Histogram'] = data['MACD'] - data['Signal']
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Fiyat
            ax1.plot(data.index, data['Close'], label=symbol, color='black', linewidth=2)
            ax1.set_title(f'{symbol} - Fiyat', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Fiyat ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # MACD
            ax2.plot(data.index, data['MACD'], label='MACD', color='blue', linewidth=1)
            ax2.plot(data.index, data['Signal'], label='Signal', color='red', linewidth=1)
            ax2.bar(data.index, data['Histogram'], label='Histogram', color='gray', alpha=0.3)
            ax2.set_title('MACD', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Tarih')
            ax2.set_ylabel('MACD')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            
            plt.tight_layout()
            dosya = f'macd_{symbol}.png'
            plt.savefig(dosya, dpi=100)
            plt.close()
            
            return f"✅ MACD grafiği: {dosya}"
        except Exception as e:
            return f"❌ Hata: {str(e)}"
    
    def rsi_grafik(self, symbol, period="3mo"):
        """RSI grafiği"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            if data.empty:
                return "❌ Veri alınamadı"
            
            # RSI hesapla
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Fiyat
            ax1.plot(data.index, data['Close'], label=symbol, color='black', linewidth=2)
            ax1.set_title(f'{symbol} - Fiyat', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Fiyat ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # RSI
            ax2.plot(data.index, data['RSI'], label='RSI(14)', color='blue', linewidth=2)
            ax2.axhline(y=70, color='r', linestyle='--', linewidth=1, label='Overbought (70)')
            ax2.axhline(y=30, color='g', linestyle='--', linewidth=1, label='Oversold (30)')
            ax2.fill_between(data.index, 70, 100, alpha=0.1, color='red')
            ax2.fill_between(data.index, 0, 30, alpha=0.1, color='green')
            ax2.set_title('RSI', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Tarih')
            ax2.set_ylabel('RSI')
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            dosya = f'rsi_{symbol}.png'
            plt.savefig(dosya, dpi=100)
            plt.close()
            
            return f"✅ RSI grafiği: {dosya}"
        except Exception as e:
            return f"❌ Hata: {str(e)}"
    
    def candlestick_grafik(self, symbol, period="1mo"):
        """Candlestick grafiği"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            if data.empty:
                return "❌ Veri alınamadı"
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            width = 0.6
            width2 = 0.05
            
            for idx, (date, row) in enumerate(data.iterrows()):
                open_p = row['Open']
                close_p = row['Close']
                high = row['High']
                low = row['Low']
                
                color = 'green' if close_p >= open_p else 'red'
                
                # High-Low çizgisi
                ax.plot([idx, idx], [low, high], color=color, linewidth=1)
                
                # Open-Close kutusu
                height = abs(close_p - open_p)
                bottom = min(open_p, close_p)
                rect = Rectangle((idx - width/2, bottom), width, height, 
                               facecolor=color, edgecolor=color, alpha=0.8)
                ax.add_patch(rect)
            
            ax.set_xlim(-1, len(data))
            ax.set_ylim(data['Low'].min() * 0.95, data['High'].max() * 1.05)
            ax.set_title(f'{symbol} - Candlestick Chart', fontsize=14, fontweight='bold')
            ax.set_xlabel('Gün')
            ax.set_ylabel('Fiyat ($)')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            dosya = f'candlestick_{symbol}.png'
            plt.savefig(dosya, dpi=100)
            plt.close()
            
            return f"✅ Candlestick grafiği: {dosya}"
        except Exception as e:
            return f"❌ Hata: {str(e)}"
    
    def hareketli_ortalama_grafik(self, symbol, period="3mo"):
        """Hareketli Ortalamaların Grafiği"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            if data.empty:
                return "❌ Veri alınamadı"
            
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['MA50'] = data['Close'].rolling(window=50).mean()
            data['MA200'] = data['Close'].rolling(window=200).mean()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            ax.plot(data.index, data['Close'], label=symbol, color='black', linewidth=2)
            ax.plot(data.index, data['MA20'], label='MA(20)', color='blue', linewidth=1)
            ax.plot(data.index, data['MA50'], label='MA(50)', color='orange', linewidth=1)
            ax.plot(data.index, data['MA200'], label='MA(200)', color='red', linewidth=1)
            
            ax.set_title(f'{symbol} - Hareketli Ortalamalar', fontsize=14, fontweight='bold')
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Fiyat ($)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            dosya = f'moving_averages_{symbol}.png'
            plt.savefig(dosya, dpi=100)
            plt.close()
            
            return f"✅ Moving Averages grafiği: {dosya}"
        except Exception as e:
            return f"❌ Hata: {str(e)}"

if __name__ == "__main__":
    grafik = GrafikAnaliz()
    print(grafik.bollinger_bands_grafik("AAPL"))
