"""📊 Dashboard Widget - /btc Analysis Display"""
import json
from src.telegram.btc_analyzer import BTCAnalyzer
from src.telegram.message_formatter import format_telegram_message

def get_btc_widget_data():
    """Dashboard için /btc widget verileri"""
    analyzer = BTCAnalyzer()
    data = analyzer.get_strong_recommendations()
    
    widget_data = {
        'title': '🔥 KESIN AL ÖNERİLERİ',
        'timestamp': data['timestamp'].isoformat(),
        'strong_buy_cryptos': [
            {
                'symbol': c['symbol'],
                'change': f"+{c['change']:.2f}%",
                'target': '+25%',
                'action': '✅ KESIN AL'
            }
            for c in data['cryptos'] if c['recommendation'] == 'STRONG_BUY'
        ][:3],
        'strong_buy_stocks': [
            {
                'symbol': s['symbol'],
                'change': f"+{s['change']:.2f}%",
                'target': '+20%',
                'action': '✅ KESIN AL'
            }
            for s in data['stocks'] if s['recommendation'] == 'STRONG_BUY'
        ][:3],
        'message': format_telegram_message(data)
    }
    
    return widget_data

if __name__ == "__main__":
    widget = get_btc_widget_data()
    print(json.dumps(widget, indent=2, ensure_ascii=False))

