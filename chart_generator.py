"""
GRAFİK OLUŞTURUCU - TELEGRAM İÇİN
Fiyat grafikleri oluşturma ve gönderme
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class ChartGenerator:
    def __init__(self):
        self.chart_dir = "charts"
        if not os.path.exists(self.chart_dir):
            os.makedirs(self.chart_dir)
        
        plt.style.use('dark_background')
        
    def get_price_history(self, symbol: str, days: int = 30) -> Dict:
        """Fiyat geçmişi al (TL)"""
        try:
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            resp = requests.get(
                "https://graph-api.btcturk.com/v1/klines/history",
                params={
                    "symbol": f"{symbol}TRY",
                    "resolution": "D" if days > 7 else "60",
                    "from": start_time // 1000,
                    "to": end_time // 1000
                },
                timeout=15
            )
            
            data = resp.json()
            if 'c' in data and len(data['c']) > 5:
                timestamps = [datetime.fromtimestamp(t) for t in data.get('t', [])]
                return {
                    'timestamps': timestamps,
                    'open': [float(x) for x in data.get('o', [])],
                    'high': [float(x) for x in data.get('h', [])],
                    'low': [float(x) for x in data.get('l', [])],
                    'close': [float(x) for x in data.get('c', [])],
                    'volume': [float(x) for x in data.get('v', [])]
                }
            return None
        except:
            return None
    
    def create_price_chart(self, symbol: str, days: int = 30) -> Optional[str]:
        """Fiyat grafiği oluştur"""
        try:
            data = self.get_price_history(symbol, days)
            if not data:
                return None
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
            fig.patch.set_facecolor('#1a1a2e')
            
            dates = data['timestamps']
            closes = data['close']
            volumes = data['volume']
            
            ax1.plot(dates, closes, color='#00d4ff', linewidth=2, label='Fiyat')
            ax1.fill_between(dates, closes, alpha=0.3, color='#00d4ff')
            
            if len(closes) >= 7:
                ma7 = np.convolve(closes, np.ones(7)/7, mode='valid')
                ax1.plot(dates[6:], ma7, color='#ffd700', linewidth=1, linestyle='--', label='MA7')
            if len(closes) >= 20:
                ma20 = np.convolve(closes, np.ones(20)/20, mode='valid')
                ax1.plot(dates[19:], ma20, color='#ff69b4', linewidth=1, linestyle='--', label='MA20')
            
            ax1.set_facecolor('#1a1a2e')
            ax1.set_title(f'{symbol}/TRY - {days} Günlük Grafik', fontsize=16, color='white', pad=20)
            ax1.set_ylabel('Fiyat (TL)', fontsize=12, color='white')
            ax1.legend(loc='upper left', fontsize=10)
            ax1.grid(True, alpha=0.3, color='gray')
            ax1.tick_params(colors='white')
            
            current_price = closes[-1]
            change = ((closes[-1] - closes[0]) / closes[0]) * 100
            change_color = '#00ff88' if change >= 0 else '#ff4444'
            ax1.text(0.02, 0.95, f'₺{current_price:,.2f} ({change:+.2f}%)', 
                    transform=ax1.transAxes, fontsize=14, color=change_color,
                    verticalalignment='top', fontweight='bold')
            
            bar_colors = ['#00ff88' if closes[i] >= closes[i-1] else '#ff4444' for i in range(1, len(closes))]
            bar_colors.insert(0, '#00ff88')
            ax2.bar(dates, volumes, color=bar_colors, alpha=0.7, width=0.8)
            ax2.set_facecolor('#1a1a2e')
            ax2.set_ylabel('Hacim', fontsize=12, color='white')
            ax2.grid(True, alpha=0.3, color='gray')
            ax2.tick_params(colors='white')
            
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            
            plt.tight_layout()
            
            filename = f"{self.chart_dir}/{symbol}_{days}d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=100, facecolor='#1a1a2e', edgecolor='none')
            plt.close()
            
            return filename
        except Exception as e:
            print(f"Chart error: {e}")
            return None
    
    def send_chart_to_telegram(self, chart_path: str, chat_id: str, caption: str = "") -> bool:
        """Grafiği Telegram'a gönder"""
        try:
            if not chart_path or not os.path.exists(chart_path):
                return False
            
            with open(chart_path, 'rb') as photo:
                resp = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                    data={'chat_id': chat_id, 'caption': caption, 'parse_mode': 'HTML'},
                    files={'photo': photo},
                    timeout=30
                )
            
            if os.path.exists(chart_path):
                os.remove(chart_path)
            
            return resp.status_code == 200
        except:
            return False
    
    def generate_and_send(self, symbol: str, chat_id: str, days: int = 30) -> bool:
        """Grafik oluştur ve gönder"""
        chart_path = self.create_price_chart(symbol, days)
        if chart_path:
            caption = f"📊 <b>{symbol}/TRY</b> - {days} Günlük Grafik"
            return self.send_chart_to_telegram(chart_path, chat_id, caption)
        return False
