"""Telegram mesaj formatı"""

def format_telegram_message(data):
    """KESIN AL önerileri formatı"""
    msg = f"🎯 *KESIN AL ÖNERİLERİ* - {data['timestamp'].strftime('%d.%m.%Y %H:%M')}\n\n"
    
    msg += "🔥 *STRONG_BUY KRİPTO (Kesin Al):*\n"
    for i, c in enumerate([x for x in data['cryptos'] if x['recommendation'] == 'STRONG_BUY'][:3], 1):
        msg += f"{i}. {c['symbol']} +{c['change']:.2f}% | Hedef: +25% | Stop: -5%\n"
    
    msg += "\n💻 *STRONG_BUY HİSSE (Kesin Al):*\n"
    for i, s in enumerate([x for x in data['stocks'] if x['recommendation'] == 'STRONG_BUY'][:3], 1):
        msg += f"{i}. {s['symbol']} +{s['change']:.2f}% | Hedef: +20% | Stop: -3%\n"
    
    msg += "\n⚠️ Kurallı oyun: Stop Loss zorunlu! Diversify edin!"
    return msg

