"""
📊 SINYAL DOĞRULUK HESAP SİSTEMİ
Signals_history.json'dan gerçek performans hesaplıyor
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class SignalAccuracy:
    """Gerçek sinyal başarı oranı hesaplama"""
    
    def __init__(self):
        self.signals_file = Path('signals_history.json')
    
    def calculate_accuracy(self) -> Dict:
        """Tüm sinyalleri analiz et"""
        try:
            with open(self.signals_file) as f:
                signals = json.load(f)
        except:
            return {'error': 'Signal dosyası bulunamadı'}
        
        win = 0
        loss = 0
        expired = 0
        total = 0
        
        by_type = {'STRONG_BUY': {'w': 0, 'l': 0, 'e': 0},
                   'BUY': {'w': 0, 'l': 0, 'e': 0},
                   'POTENTIAL': {'w': 0, 'l': 0, 'e': 0}}
        
        profit_loss = []
        
        for sig in signals:
            total += 1
            status = sig.get('status', '').upper()
            result = sig.get('result', '').upper()
            sig_type = sig.get('signal_type', 'POTENTIAL')
            pnl = sig.get('result_percent', 0)
            symbol = sig.get('symbol', 'UNKNOWN')
            
            profit_loss.append({'symbol': symbol, 'pnl': pnl, 'type': sig_type})
            
            if status == 'WIN' or result == 'HEDEF':
                win += 1
                if sig_type in by_type:
                    by_type[sig_type]['w'] += 1
            elif status == 'LOSS' or result == 'STOP':
                loss += 1
                if sig_type in by_type:
                    by_type[sig_type]['l'] += 1
            elif status == 'EXPIRED' or result == 'SÜRE DOLDU':
                expired += 1
                if sig_type in by_type:
                    by_type[sig_type]['e'] += 1
        
        # Accuracy hesapla
        accuracy = (win / total * 100) if total > 0 else 0
        avg_win = sum([p['pnl'] for p in profit_loss if p['pnl'] > 0]) / win if win > 0 else 0
        avg_loss = sum([p['pnl'] for p in profit_loss if p['pnl'] < 0]) / loss if loss > 0 else 0
        total_pnl = sum([p['pnl'] for p in profit_loss])
        
        # Sinyal türüne göre başarı
        type_accuracy = {}
        for sig_type, counts in by_type.items():
            total_type = counts['w'] + counts['l'] + counts['e']
            if total_type > 0:
                acc = (counts['w'] / total_type * 100)
                type_accuracy[sig_type] = {
                    'win': counts['w'],
                    'loss': counts['l'],
                    'expired': counts['e'],
                    'accuracy': round(acc, 1)
                }
        
        return {
            'total_signals': total,
            'wins': win,
            'losses': loss,
            'expired': expired,
            'accuracy_percent': round(accuracy, 1),
            'avg_winning_pnl': round(avg_win, 2),
            'avg_losing_pnl': round(avg_loss, 2),
            'total_pnl_percent': round(total_pnl, 2),
            'by_signal_type': type_accuracy,
            'profit_factor': round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0,
            'message': self._generate_message(accuracy, win, total)
        }
    
    def _generate_message(self, accuracy: float, wins: int, total: int) -> str:
        """Telegram mesajı oluştur"""
        msg = f"📊 SINYAL PERFORMANS RAPORU\n"
        msg += f"{'='*40}\n"
        msg += f"📈 Toplam Sinyal: {total}\n"
        msg += f"✅ Kazanç: {wins}\n"
        msg += f"❌ Kayıp: {total - wins}\n"
        msg += f"🎯 Başarı Oranı: {accuracy:.1f}%\n"
        
        if accuracy < 50:
            msg += f"\n⚠️  UYARI: Accuracy %50'nin altında!\n"
            msg += f"Random'dan daha kötü!"
        elif accuracy < 60:
            msg += f"\n⚡ Geliştirme gerekli\n"
        else:
            msg += f"\n✨ İyi performans!\n"
        
        return msg
    
    def get_telegram_report(self) -> str:
        """Telegram için detaylı rapor"""
        data = self.calculate_accuracy()
        if 'error' in data:
            return f"❌ {data['error']}"
        
        msg = f"📊 SİSTEM DOĞRULUK ANALİZİ\n"
        msg += f"{'='*45}\n"
        msg += f"📌 Toplam Test: {data['total_signals']} sinyal\n"
        msg += f"✅ Başarılı: {data['wins']} ({data['accuracy_percent']:.1f}%)\n"
        msg += f"❌ Başarısız: {data['losses']}\n"
        msg += f"⏱️  Süresi Doldu: {data['expired']}\n"
        msg += f"\n💰 Ortalama Kazanç: {data['avg_winning_pnl']:.2f}%\n"
        msg += f"📉 Ortalama Kayıp: {data['avg_losing_pnl']:.2f}%\n"
        msg += f"🔄 Profit Factor: {data['profit_factor']}x\n"
        msg += f"💵 Toplam P&L: {data['total_pnl_percent']:.2f}%\n"
        msg += f"\n{'SINYAL TÜRÜNE GÖRE':-^45}\n"
        
        for sig_type, stats in data['by_signal_type'].items():
            msg += f"\n{sig_type}:\n"
            msg += f"  ✅ {stats['win']} | ❌ {stats['loss']} | ⏱️  {stats['expired']}\n"
            msg += f"  🎯 Doğruluk: {stats['accuracy']:.1f}%\n"
        
        return msg
