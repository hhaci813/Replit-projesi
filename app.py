"""Extended Flask app with global markets"""
from flask import Flask, jsonify
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/')
def home():
    try:
        with open('static/advanced_dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<h1>Hata: {e}</h1>"

@app.route('/api/btcturk-analysis')
def btcturk_analysis():
    try:
        from btcturk_market_scanner import BTCTurkMarketScanner
        scanner = BTCTurkMarketScanner()
        return jsonify(scanner.get_analysis_json())
    except Exception as e:
        return jsonify({'assets': [], 'error': str(e)})

@app.route('/api/global-markets')
def global_markets():
    """Global markets - S&P 500, DAX, NIKKEI, vb"""
    try:
        from global_markets_analyzer import GlobalMarketsAnalyzer
        analyzer = GlobalMarketsAnalyzer()
        summary = analyzer.get_market_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/sectors')
def sectors():
    """Sektör analizi"""
    try:
        from global_markets_analyzer import SectorAnalyzer
        analyzer = SectorAnalyzer()
        sectors = analyzer.get_sector_performance()
        return jsonify({'sectors': sectors})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/expert-opinions/<query>')
def expert_opinions(query):
    """Expert yorumları - BTC, AAPL, vb"""
    try:
        from expert_sentiment_extractor import ExpertSentimentExtractor
        extractor = ExpertSentimentExtractor()
        result = extractor.extract_expert_opinions(query, days=7)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/recommendation/<asset>/<float:technical>/<float:sentiment>/<float:momentum>')
def get_recommendation(asset, technical, sentiment, momentum):
    """Kar/Zarar önerisi"""
    try:
        from recommendation_engine import RecommendationEngine
        engine = RecommendationEngine()
        rec = engine.generate_recommendation(asset, technical, sentiment, momentum)
        return jsonify(rec)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
