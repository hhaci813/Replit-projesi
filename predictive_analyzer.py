"""🔮 PREDICTIVE ANALYZER - YÜKSELECEK KRİPTOLARI TESPİT ET
Yükselmiş değil, YÜKSELECEK olanları bul!
"""
import requests
from datetime import datetime
import json

class PredictiveAnalyzer:
    """Yükselecek kriptoları tespit eden analiz motoru"""
    
    def __init__(self):
        self.btcturk_url = "https://api.btcturk.com/api/v2/ticker"
    
    def get_btcturk_data(self):
        """BTCTurk verilerini al"""
        try:
            resp = requests.get(self.btcturk_url, timeout=15)
            return resp.json().get('data', [])
        except:
            return []
    
    def analyze_potential_risers(self):
        """
        YÜKSELECEK kriptoları tespit et:
        1. Hacim artışı var ama fiyat henüz düşük/stabil
        2. Fiyat dip yapmış, toparlanma başlıyor
        3. Düşük fiyat değişimi ama yüksek hacim = birikim
        4. Negatiften pozitife dönenler
        """
        tickers = self.get_btcturk_data()
        
        potential_risers = []
        
        for t in tickers:
            if not isinstance(t, dict):
                continue
            
            pair = t.get('pairNormalized', '')
            if 'TRY' not in pair:
                continue
            
            symbol = pair.split('_')[0]
            price = float(t.get('last', 0))
            change = float(t.get('dailyPercent', 0))
            volume = float(t.get('volume', 0))
            high = float(t.get('high', 0))
            low = float(t.get('low', 0))
            bid = float(t.get('bid', 0))
            ask = float(t.get('ask', 0))
            
            if price <= 0:
                continue
            
            # Skor hesaplama
            score = 0
            signals = []
            
            # 1. ACCUMULATION: Düşük değişim + Yüksek hacim = Birikim
            if -3 < change < 3 and volume > 1000000:
                score += 25
                signals.append("📦 Birikim sinyali (düşük değişim + yüksek hacim)")
            
            # 2. OVERSOLD BOUNCE: Düşüşten toparlanma
            if -10 < change < 0 and volume > 500000:
                score += 20
                signals.append("📉 Dip noktası (düşüşten toparlanma potansiyeli)")
            
            # 3. BREAKOUT SETUP: Fiyat dibe yakın ama hacim artıyor
            if high > 0 and low > 0:
                price_position = (price - low) / (high - low) if high != low else 0.5
                if price_position < 0.3 and volume > 500000:
                    score += 30
                    signals.append("🎯 Breakout setup (dipten kırılım potansiyeli)")
            
            # 4. REVERSAL: Negatiften pozitife dönüş başlangıcı
            if -5 < change < 2 and change > -2:
                score += 15
                signals.append("🔄 Reversal sinyali (dönüş başlangıcı)")
            
            # 5. VOLUME SPIKE: Ani hacim artışı
            if volume > 5000000 and abs(change) < 5:
                score += 20
                signals.append("📊 Hacim patlaması (büyük oyuncular aktif)")
            
            # 6. SPREAD ANALYSIS: Düşük spread = likidite
            if bid > 0 and ask > 0:
                spread = ((ask - bid) / bid) * 100
                if spread < 0.5:
                    score += 10
                    signals.append("💧 Yüksek likidite")
            
            # 7. HENÜZ YÜKSELMEMIŞ: Değişim düşük
            if change < 5:
                score += 10
                signals.append("⏳ Henüz yükselmemiş")
            
            # Eğer skor yeterliyse listeye ekle
            if score >= 40 and signals:
                # Potansiyel kar hesapla
                if high > price:
                    potential_gain = ((high - price) / price) * 100
                else:
                    potential_gain = 15  # Minimum hedef
                
                potential_risers.append({
                    'symbol': symbol,
                    'price': price,
                    'change': change,
                    'volume': volume,
                    'score': score,
                    'signals': signals,
                    'potential_gain': round(min(potential_gain, 50), 1),
                    'risk': self._calculate_risk(change, volume),
                    'recommendation': 'POTENTIAL_BUY' if score >= 60 else 'WATCH'
                })
        
        # Skora göre sırala
        return sorted(potential_risers, key=lambda x: x['score'], reverse=True)
    
    def _calculate_risk(self, change, volume):
        """Risk seviyesi hesapla"""
        risk = 5
        if abs(change) > 10:
            risk += 2
        if volume < 100000:
            risk += 2
        if change < -5:
            risk += 1
        return min(risk, 10)
    
    def get_best_opportunities(self, limit=10):
        """En iyi fırsatları getir"""
        all_potentials = self.analyze_potential_risers()
        return all_potentials[:limit]
    
    def format_telegram_message(self, opportunities):
        """Telegram mesajı formatla"""
        if not opportunities:
            return "⚠️ Şu an potansiyel yükseliş sinyali bulunamadı."
        
        now = datetime.now()
        msg = f"""🔮 <b>YÜKSELECEK KRİPTO ANALİZİ</b>
📅 {now.strftime('%d.%m.%Y %H:%M')}

<b>Henüz yükselmemiş ama yükselme potansiyeli olan kriptolar:</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for i, opp in enumerate(opportunities[:5], 1):
            rec_emoji = "🎯" if opp['recommendation'] == 'POTENTIAL_BUY' else "👀"
            
            msg += f"""
{rec_emoji} <b>{i}. {opp['symbol']}</b>
   💰 Fiyat: {opp['price']:.4f} TRY
   📊 Değişim: {'+' if opp['change'] > 0 else ''}{opp['change']:.2f}%
   🎯 Potansiyel: +{opp['potential_gain']}%
   📈 Skor: {opp['score']}/100
   ⚠️ Risk: {opp['risk']}/10
   
   <b>Sinyaller:</b>
"""
            for signal in opp['signals'][:3]:
                msg += f"   • {signal}\n"
        
        msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ <b>UYARI:</b>
Bu tahminler teknik analize dayanır.
Stop-loss ZORUNLU! DYOR (Kendi araştırmanı yap)

🔄 <b>Güncelleme:</b> Her 2 saatte
"""
        
        return msg


def run_predictive_analysis():
    """Predictive analizi çalıştır"""
    analyzer = PredictiveAnalyzer()
    opportunities = analyzer.get_best_opportunities(10)
    
    print("🔮 YÜKSELECEK KRİPTO ANALİZİ")
    print("=" * 60)
    print("Henüz yükselmemiş ama potansiyeli olanlar:\n")
    
    if not opportunities:
        print("⚠️ Şu an potansiyel sinyal bulunamadı")
        return []
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{'🎯' if opp['recommendation'] == 'POTENTIAL_BUY' else '👀'} {i}. {opp['symbol']}")
        print(f"   Fiyat: {opp['price']:.4f} TRY")
        print(f"   Günlük Değişim: {'+' if opp['change'] > 0 else ''}{opp['change']:.2f}%")
        print(f"   Potansiyel Kazanç: +{opp['potential_gain']}%")
        print(f"   Skor: {opp['score']}/100")
        print(f"   Risk: {opp['risk']}/10")
        print(f"   Tavsiye: {opp['recommendation']}")
        print(f"   Sinyaller:")
        for signal in opp['signals']:
            print(f"      • {signal}")
    
    return opportunities


if __name__ == '__main__':
    run_predictive_analysis()

