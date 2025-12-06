"""🐋 WHALE TRACKER - BÜYÜK İŞLEM TAKİBİ
Blockchain'de büyük cüzdan hareketlerini takip et
"""
import requests
from datetime import datetime

class WhaleTracker:
    """Büyük işlem takipçisi"""
    
    def __init__(self):
        self.whale_alert_api = "https://api.whale-alert.io/v1/transactions"
        # Whale Alert API key gerekiyor - ücretsiz tier mevcut
    
    def get_btc_whale_transactions(self):
        """BTC büyük işlemlerini simüle et (API key olmadan)"""
        # Gerçek API için whale-alert.io'dan key alınmalı
        # Şimdilik blockchain.info'dan büyük işlemleri çekeceğiz
        
        try:
            # Son blokları kontrol et
            resp = requests.get(
                "https://blockchain.info/unconfirmed-transactions?format=json",
                timeout=10
            )
            
            if resp.status_code != 200:
                return self._get_simulated_whale_data()
            
            data = resp.json()
            txs = data.get('txs', [])
            
            whale_txs = []
            for tx in txs:
                total_btc = sum(out.get('value', 0) for out in tx.get('out', [])) / 100000000
                
                if total_btc >= 10:  # 10+ BTC = whale
                    whale_txs.append({
                        'hash': tx.get('hash', '')[:16] + '...',
                        'amount_btc': round(total_btc, 2),
                        'amount_usd': round(total_btc * 100000, 0),  # Yaklaşık
                        'type': 'TRANSFER',
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
            
            return whale_txs[:10]
            
        except Exception as e:
            return self._get_simulated_whale_data()
    
    def _get_simulated_whale_data(self):
        """API erişimi yoksa simüle veri"""
        return [
            {'hash': 'Simulated data', 'amount_btc': 0, 'type': 'NO_API', 'note': 'Gerçek veri için Whale Alert API gerekli'}
        ]
    
    def analyze_whale_activity(self):
        """Whale aktivitesini analiz et"""
        txs = self.get_btc_whale_transactions()
        
        if not txs or txs[0].get('type') == 'NO_API':
            return {
                'status': 'NO_DATA',
                'message': 'Whale verisi alınamadı',
                'recommendation': 'NEUTRAL'
            }
        
        total_volume = sum(tx['amount_btc'] for tx in txs)
        avg_size = total_volume / len(txs) if txs else 0
        
        # Whale aktivitesi yorumu
        if total_volume > 1000:
            activity = 'VERY_HIGH'
            recommendation = 'Dikkat - Büyük hareketler var'
        elif total_volume > 500:
            activity = 'HIGH'
            recommendation = 'Orta düzey whale aktivitesi'
        elif total_volume > 100:
            activity = 'MODERATE'
            recommendation = 'Normal aktivite'
        else:
            activity = 'LOW'
            recommendation = 'Düşük whale aktivitesi'
        
        return {
            'status': 'OK',
            'total_volume_btc': round(total_volume, 2),
            'transaction_count': len(txs),
            'avg_size_btc': round(avg_size, 2),
            'activity_level': activity,
            'recommendation': recommendation,
            'recent_transactions': txs[:5]
        }
    
    def get_exchange_flows(self):
        """Borsa giriş/çıkışları (simüle)"""
        # Gerçek veri için Glassnode, CryptoQuant API gerekli
        return {
            'net_flow': 'OUTFLOW',  # Borsalardan çıkış = bullish
            'message': 'Borsalardan net çıkış (bullish sinyal)',
            'note': 'Gerçek veri için Glassnode/CryptoQuant API gerekli'
        }


if __name__ == '__main__':
    tracker = WhaleTracker()
    
    print("🐋 WHALE TRACKER\n")
    
    result = tracker.analyze_whale_activity()
    
    print(f"Durum: {result['status']}")
    print(f"Toplam Hacim: {result.get('total_volume_btc', 0)} BTC")
    print(f"İşlem Sayısı: {result.get('transaction_count', 0)}")
    print(f"Aktivite: {result.get('activity_level', 'N/A')}")
    print(f"Yorum: {result.get('recommendation', '')}")
