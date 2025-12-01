"""📊 Telegram Global Recommendations - Dünya borsası önerileri"""
from telegram_service import TelegramService
from global_markets_analyzer import GlobalMarketsAnalyzer, SectorAnalyzer
from expert_sentiment_extractor import ExpertSentimentExtractor
from recommendation_engine import RecommendationEngine
from datetime import datetime

def send_global_recommendations():
    """Dünya borsası global önerileri gönder"""
    try:
        telegram = TelegramService()
        
        # 1. Global Markets Status
        analyzer = GlobalMarketsAnalyzer()
        summary = analyzer.get_market_summary()
        
        msg = f"""
╔═══════════════════════════════════════════╗
║ 🌍 GLOBAL MARKETS ANALYSIS - {datetime.now().strftime('%d.%m.%Y')}
╚═══════════════════════════════════════════╝

📊 GLOBAL MARKET STATUS: {summary['overall']}
   Avarage Change: {summary['avg_change']:+.2f}%
   ✅ Up: {summary['rising_count']} indices
   📉 Down: {summary['falling_count']} indices

📈 MAJOR INDICES:
"""
        
        for idx in summary['indices'][:5]:  # Top 5
            msg += f"   {idx['emoji']} {idx['index']:12} {idx['change']:+6.2f}% (RSI: {idx['rsi']:.0f})\n"
        
        # 2. Sektor Analizi
        sector_analyzer = SectorAnalyzer()
        sectors = sector_analyzer.get_sector_performance()
        
        msg += "\n🏭 SECTOR PERFORMANCE (1 Year):\n"
        for sector in sectors[:5]:
            msg += f"   {sector['emoji']} {sector['sector']:15} {sector['year_change']:+6.1f}% ({sector['rating']})\n"
        
        # 3. Expert Opinions & Recommendations
        extractor = ExpertSentimentExtractor()
        
        msg += "\n📰 EXPERT SENTIMENT:\n"
        
        for query in ['Bitcoin', 'Apple', 'Tesla']:
            result = extractor.extract_expert_opinions(query, days=7)
            if result.get('opinions'):
                consensus = result.get('consensus', 'NEUTRAL')
                msg += f"   {query:12} → {consensus}\n"
        
        # 4. Investment Recommendations
        msg += """
💡 INVESTMENT RECOMMENDATIONS:

🟢 BUY SIGNALS:
   • Technology sector showing strength
   • Positive sentiment from experts
   • RSI overbought in some indices

🔴 SELL SIGNALS:
   • Watch energy sector volatility
   • Mixed expert opinions
   • Some indices showing weakness

🟡 HOLD POSITIONS:
   • Wait for clearer market direction
   • Monitor global economic news
   • Consider profit-taking

⚠️ RISK MANAGEMENT:
   • Use stop-loss at -5% from entry
   • Don't go all-in on single asset
   • Diversify across sectors
   • Follow expert consensus

📊 PROFIT/LOSS POTENTIAL:
   🟢 Strong Buy: +8% to +15%
   🟢 Buy: +3% to +8%
   🟡 Hold: -2% to +3%
   🔴 Sell: -8% to -3%
   🔴 Strong Sell: -15% to -8%

═══════════════════════════════════════════
🚀 Dashboard: http://localhost:5000/
📱 For details: /api/global-markets
"""
        
        telegram._send_message(msg)
        print("✅ Global recommendations Telegram'a gönderildi")
        return True
    
    except Exception as e:
        print(f"❌ Global recommendations hatası: {e}")
        return False

if __name__ == "__main__":
    send_global_recommendations()
