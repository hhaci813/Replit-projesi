"""
Kompakt Telegram Mesaj Sistemi
- Kısa ve öz mesajlar
- Sadece actionable bilgi
- Grafik yok, metin özeti var
"""

import os
import requests
from datetime import datetime
import pytz

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def get_tr_time():
    """Türkiye saati"""
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        return datetime.now(tr_tz).strftime('%H:%M')
    except:
        return datetime.now().strftime('%H:%M')

def send_compact(message):
    """Kısa mesaj gönder"""
    if not BOT_TOKEN or not CHAT_ID:
        return False
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    resp = requests.post(url, json={
        'chat_id': CHAT_ID, 
        'text': message, 
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }, timeout=15)
    return resp.status_code == 200

def signal_alert(symbol, action, price, target=None, stop=None, reason=""):
    """
    Kısa sinyal mesajı
    action: BUY, SELL, HOLD, WATCH
    """
    emojis = {
        'BUY': '🟢 AL',
        'STRONG_BUY': '🟢🟢 GÜÇLÜ AL',
        'SELL': '🔴 SAT',
        'STRONG_SELL': '🔴🔴 GÜÇLÜ SAT',
        'HOLD': '⚪ TUT',
        'WATCH': '👀 İZLE'
    }
    
    action_text = emojis.get(action.upper(), f'📊 {action}')
    time_now = get_tr_time()
    
    msg = f"{action_text} <b>{symbol}</b>\n"
    msg += f"💰 ₺{price:,.2f}"
    
    if target:
        msg += f" → ₺{target:,.2f}"
    if stop:
        msg += f" | Stop: ₺{stop:,.2f}"
    
    if reason:
        msg += f"\n💡 {reason}"
    
    msg += f"\n⏰ {time_now}"
    
    return send_compact(msg)

def portfolio_summary(total_value, change_pct, top_movers):
    """
    Kısa portföy özeti
    top_movers: [{'symbol': 'XRP', 'change': 5.2}, ...]
    """
    time_now = get_tr_time()
    
    emoji = '📈' if change_pct > 0 else '📉' if change_pct < 0 else '➡️'
    
    msg = f"💼 <b>PORTFÖY</b> {emoji}\n"
    msg += f"₺{total_value:,.0f} ({change_pct:+.1f}%)\n"
    
    if top_movers:
        for m in top_movers[:3]:
            e = '🟢' if m['change'] > 0 else '🔴'
            msg += f"{e} {m['symbol']}: {m['change']:+.1f}%\n"
    
    msg += f"⏰ {time_now}"
    
    return send_compact(msg)

def quick_alert(title, message):
    """Hızlı uyarı"""
    time_now = get_tr_time()
    msg = f"⚡ <b>{title}</b>\n{message}\n⏰ {time_now}"
    return send_compact(msg)

def market_pulse(btc_change, fear_greed, altcoin_season):
    """Piyasa nabzı - tek satır"""
    time_now = get_tr_time()
    
    btc_emoji = '🟢' if btc_change > 0 else '🔴'
    
    msg = f"📊 <b>PİYASA</b>\n"
    msg += f"{btc_emoji} BTC: {btc_change:+.1f}% | "
    msg += f"😱 F&G: {fear_greed} | "
    msg += f"🔷 Alt: {altcoin_season}\n"
    msg += f"⏰ {time_now}"
    
    return send_compact(msg)

def coin_analysis_compact(symbol, price, quantum_score, action, key_points):
    """
    Kompakt coin analizi
    key_points: ["Balina alımı var", "RSI aşırı satım", ...]
    """
    time_now = get_tr_time()
    
    if quantum_score >= 75:
        score_emoji = "🟢"
    elif quantum_score >= 50:
        score_emoji = "🟡"
    else:
        score_emoji = "🔴"
    
    msg = f"{score_emoji} <b>{symbol}</b> | Q:{quantum_score}/100\n"
    msg += f"💰 ₺{price:,.2f} | {action}\n"
    
    if key_points:
        for point in key_points[:3]:
            msg += f"• {point}\n"
    
    msg += f"⏰ {time_now}"
    
    return send_compact(msg)

def prediction_result(symbol, direction, entry, exit_price, result):
    """Tahmin sonucu bildirimi"""
    pct = ((exit_price - entry) / entry) * 100
    
    if result == 'WIN':
        emoji = '✅'
        text = 'KAZANDI'
    else:
        emoji = '❌'
        text = 'KAYBETTİ'
    
    msg = f"{emoji} <b>{symbol}</b> {text}\n"
    msg += f"Giriş: ₺{entry:,.2f} → Çıkış: ₺{exit_price:,.2f}\n"
    msg += f"Sonuç: {pct:+.1f}%"
    
    return send_compact(msg)


if __name__ == "__main__":
    print("Kompakt Telegram sistemi hazır!")
    
    signal_alert("XRP", "BUY", 85.36, target=98.16, stop=76.82, reason="Balina biriktirme")
