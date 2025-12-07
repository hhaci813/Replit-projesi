#!/usr/bin/env python3
"""
🚀 BTC TURK RENDER BOTU
Render.com için optimize edilmiş BTC Turk botu
"""

import requests
import time
from datetime import datetime

print("=" * 50)
print("🤖 BTC TURK CANLI BOTU")
print(f"⏰ Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

def get_crypto_price(pair):
    """BTC Turk'ten kripto fiyatı al"""
    try:
        url = f"https://api.btcturk.com/api/v2/ticker?pairSymbol={pair}"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data['data'][0]
    except Exception as e:
        print(f"❌ {pair} hatası: {e}")
        return None

# Ana döngü
counter = 0
while True:
    try:
        counter += 1
        print(f"\n📊 GÜNCELLEME #{counter}")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 40)
        
        # BTC
        btc = get_crypto_price("BTCTRY")
        if btc:
            btc_price = float(btc['last'])
            btc_change = float(btc['daily'])
            btc_symbol = "📈" if btc_change > 0 else "📉" if btc_change < 0 else "➡️"
            print(f"{btc_symbol} BTC/TRY: ₺{btc_price:,.0f} ({btc_change:+.2f}%)")
        
        # ETH
        eth = get_crypto_price("ETHTRY")
        if eth:
            eth_price = float(eth['last'])
            eth_change = float(eth['daily'])
            eth_symbol = "📈" if eth_change > 0 else "📉" if eth_change < 0 else "➡️"
            print(f"{eth_symbol} ETH/TRY: ₺{eth_price:,.0f} ({eth_change:+.2f}%)")
        
        # XRP
        xrp = get_crypto_price("XRPTRY")
        if xrp:
            xrp_price = float(xrp['last'])
            xrp_change = float(xrp['daily'])
            xrp_symbol = "📈" if xrp_change > 0 else "📉" if xrp_change < 0 else "➡️"
            print(f"{xrp_symbol} XRP/TRY: ₺{xrp_price:,.0f} ({xrp_change:+.2f}%)")
        
        print(f"⏳ 60 saniye sonra güncellenecek...")
        
        # 60 saniye bekle
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Bot durduruldu")
        break
    except Exception as e:
        print(f"⚠️ Sistem hatası: {e}")
        time.sleep(30)
