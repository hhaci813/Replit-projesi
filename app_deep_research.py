"""Extended Flask app with Deep Research endpoints"""
from flask import Flask, jsonify

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Import existing endpoints
from app import home, btcturk_analysis, global_markets, sectors, expert_opinions, get_recommendation

@app.route('/api/deep-research/<asset>')
def deep_research(asset):
    """Deep research report for any asset"""
    try:
        from deep_research_analyzer import DeepResearchAnalyzer
        analyzer = DeepResearchAnalyzer()
        
        if asset.upper() == 'BTC':
            research = analyzer.analyze_btc_deep()
            return jsonify(research)
        else:
            return jsonify({'error': 'Currently supporting BTC deep research'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/scrape-news/<keyword>')
def scrape_news(keyword):
    """Scrape crypto news"""
    try:
        from advanced_web_scraper import AdvancedWebScraper
        scraper = AdvancedWebScraper()
        news = scraper.scrape_crypto_news(keyword, limit=20)
        return jsonify({'keyword': keyword, 'articles': news, 'count': len(news)})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/whale-activity')
def whale_activity():
    """Whale transactions and sentiment"""
    try:
        from deep_research_analyzer import DeepResearchAnalyzer
        analyzer = DeepResearchAnalyzer()
        whales = analyzer._analyze_whale_activity()
        return jsonify(whales)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/social-signals')
def social_signals():
    """Social media sentiment and signals"""
    try:
        from advanced_web_scraper import AdvancedWebScraper
        scraper = AdvancedWebScraper()
        socials = scraper.scrape_btcturk_socials()
        return jsonify(socials)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
