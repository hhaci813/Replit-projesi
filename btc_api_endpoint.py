"""📊 /btc Komutu - Flask API Endpoint"""
from flask import Blueprint, jsonify
from telegram_btc_bot import StrongBuyAnalyzer
from datetime import datetime

btc_bp = Blueprint('btc', __name__, url_prefix='/api/btc')

@btc_bp.route('/analysis', methods=['GET'])
def get_btc_analysis():
    """GET /api/btc/analysis - STRONG_BUY önerileri"""
    try:
        analyzer = StrongBuyAnalyzer()
        data = analyzer.get_strong_recommendations()
        
        # Format response
        response = {
            'timestamp': data['timestamp'].isoformat(),
            'strong_buy': {
                'cryptos': [
                    {
                        'symbol': c['symbol'],
                        'change': round(c['change'], 2),
                        'price': c['price'],
                        'target': round(c['profit_target'], 2),
                        'score': c['score'],
                        'recommendation': c['recommendation']
                    }
                    for c in data['cryptos'] if c['recommendation'] == 'STRONG_BUY'
                ],
                'stocks': [
                    {
                        'symbol': s['symbol'],
                        'change': round(s['change'], 2),
                        'price': round(s['price'], 2),
                        'target': round(s['profit_target'], 2),
                        'score': s['score'],
                        'recommendation': s['recommendation']
                    }
                    for s in data['stocks'] if s['recommendation'] == 'STRONG_BUY'
                ]
            },
            'buy': {
                'cryptos': [c['symbol'] for c in data['cryptos'] if c['recommendation'] == 'BUY'][:5],
                'stocks': [s['symbol'] for s in data['stocks'] if s['recommendation'] == 'BUY'][:5]
            },
            'message': 'STRONG_BUY = Kesin al, BUY = Fırsat varsa al'
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@btc_bp.route('/telegram-message', methods=['GET'])
def get_telegram_message():
    """GET /api/btc/telegram-message - Telegram formatı"""
    try:
        analyzer = StrongBuyAnalyzer()
        data = analyzer.get_strong_recommendations()
        message = analyzer.format_telegram_message(data)
        
        return jsonify({
            'message': message,
            'timestamp': data['timestamp'].isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@btc_bp.route('/send-telegram', methods=['POST'])
def send_to_telegram():
    """POST /api/btc/send-telegram - Telegram'a gönder"""
    try:
        analyzer = StrongBuyAnalyzer()
        data = analyzer.get_strong_recommendations()
        message = analyzer.format_telegram_message(data)
        
        success = analyzer.send_telegram(message)
        
        return jsonify({
            'success': success,
            'message': 'Telegram\'a gönderildi' if success else 'Hata oluştu',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

