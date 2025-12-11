"""
Telegram Kompakt Mesaj Sistemi
Kısa, öz ve işe yarar mesajlar
"""

import os
import requests
from datetime import datetime
import pytz

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def get_tr_time():
    """Türkiye saatini al"""
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        return datetime.now(tr_tz).strftime('%H:%M')
    except:
        return datetime.now().strftime('%H:%M')

def send_compact(text):
    """Kompakt mesaj gönder"""
    if not BOT_TOKEN or not CHAT_ID:
        return False
    
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    resp = requests.post(url, json={
        'chat_id': CHAT_ID, 
        'text': text, 
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }, timeout=15)
    return resp.status_code == 200

def signal_alert(symbol, action, price, target=None, stop=None, reason=""):
    """Sinyal uyarısı - 4 satır max"""
    now = get_tr_time()
    
    if action.upper() in ['AL', 'BUY', 'STRONG_BUY']:
        emoji = "🟢"
        act = "AL"
    elif action.upper() in ['SAT', 'SELL', 'STRONG_SELL']:
        emoji = "🔴"
        act = "SAT"
    else:
        emoji = "🟡"
        act = "İZLE"
    
    msg = f"{emoji} <b>{symbol}</b> → {act} | ₺{price:,.2f}\n"
    
    if target:
        msg += f"🎯 Hedef: ₺{target:,.2f}\n"
    if stop:
        msg += f"⛔ Stop: ₺{stop:,.2f}\n"
    if reason:
        msg += f"💡 {reason[:50]}"
    
    return send_compact(msg)

def portfolio_summary(total_try, change_pct, top_coins):
    """Portföy özeti - kısa"""
    now = get_tr_time()
    emoji = "📈" if change_pct >= 0 else "📉"
    
    msg = f"💼 <b>Portföy</b> {now}\n"
    msg += f"{emoji} ₺{total_try:,.0f} ({change_pct:+.1f}%)\n"
    
    for coin, pct in top_coins[:3]:
        e = "🟢" if pct >= 0 else "🔴"
        msg += f"{e} {coin}: {pct:+.1f}%  "
    
    return send_compact(msg)

def price_alert(symbol, price, change_pct, alert_type="info"):
    """Fiyat uyarısı - 2 satır"""
    if alert_type == "pump":
        emoji = "🚀"
    elif alert_type == "dump":
        emoji = "💥"
    elif change_pct > 0:
        emoji = "📈"
    else:
        emoji = "📉"
    
    msg = f"{emoji} <b>{symbol}</b>: ₺{price:,.2f} ({change_pct:+.1f}%)"
    return send_compact(msg)

def quick_update(coins_data):
    """Hızlı piyasa özeti - tek mesaj"""
    now = get_tr_time()
    
    msg = f"📊 <b>Piyasa</b> {now}\n"
    
    for coin in coins_data[:5]:
        symbol = coin.get('symbol', '')
        price = coin.get('price', 0)
        change = coin.get('change', 0)
        emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
        msg += f"{emoji} {symbol}: ₺{price:,.0f} ({change:+.1f}%)\n"
    
    return send_compact(msg)

def prediction_result(symbol, direction, entry, exit_price, result):
    """Tahmin sonucu - 2 satır"""
    emoji = "✅" if result == "WIN" else "❌"
    pct = ((exit_price - entry) / entry) * 100
    
    msg = f"{emoji} <b>{symbol}</b> tahmini: {result}\n"
    msg += f"Giriş: ₺{entry:,.2f} → Çıkış: ₺{exit_price:,.2f} ({pct:+.1f}%)"
    
    return send_compact(msg)

def daily_summary(total_predictions, accuracy, top_winner, top_loser):
    """Günlük özet - 4 satır"""
    now = get_tr_time()
    
    msg = f"📅 <b>Günlük Özet</b> {now}\n"
    msg += f"🎯 Başarı: %{accuracy:.0f} ({total_predictions} tahmin)\n"
    
    if top_winner:
        msg += f"🏆 En iyi: {top_winner[0]} +%{top_winner[1]:.1f}\n"
    if top_loser:
        msg += f"💔 En kötü: {top_loser[0]} %{top_loser[1]:.1f}"
    
    return send_compact(msg)

def actionable_only(coins_list):
    """Sadece aksiyon gerektiren coinler"""
    now = get_tr_time()
    
    actionable = []
    for coin in coins_list:
        change = coin.get('change', 0)
        if abs(change) > 5:
            actionable.append(coin)
    
    if not actionable:
        return False
    
    msg = f"⚡ <b>Aksiyon</b> {now}\n"
    for coin in actionable[:5]:
        symbol = coin.get('symbol', '')
        change = coin.get('change', 0)
        if change > 5:
            msg += f"🚀 {symbol}: +%{change:.1f} → Kâr al?\n"
        else:
            msg += f"🚨 {symbol}: %{change:.1f} → Stop?\n"
    
    return send_compact(msg)


if __name__ == "__main__":
    print("Telegram Kompakt Sistem Test")
    signal_alert("XRP", "AL", 85.36, target=98.16, stop=77.0, reason="Balina biriktirme")
