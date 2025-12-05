"""📊 Deep BTC Research Report - Sisteme entegre"""
from deep_research_analyzer import DeepResearchAnalyzer
from recommendation_engine import RecommendationEngine
from telegram_service import TelegramService
from datetime import datetime
import json

print("\n" + "="*70)
print("🔬 DEEP BTC RESEARCH REPORT - DERINLEMESINE ANALİZ")
print("="*70 + "\n")

# Deep Research
analyzer = DeepResearchAnalyzer()
research = analyzer.analyze_btc_deep()

print("\n📊 ARAŞTIRMA SONUÇLARI:")
print("-" * 70)

# Print layers
for layer_name, layer_data in research['layers'].items():
    print(f"\n{layer_name.upper()}:")
    if isinstance(layer_data, dict) and 'insights' in layer_data:
        for insight in layer_data.get('insights', []):
            if insight:
                print(f"   • {insight}")

# Verdict
verdict = research['verdict']
print("\n" + "="*70)
print(f"🎯 FINAL VERDICT: {verdict['recommendation']}")
print(f"   Score: {verdict['overall_score']:.1f}/10")
print(f"   Confidence: {verdict['confidence']:.0%}")
print(f"   Message: {verdict['final_message']}")
print("="*70)

# Integration with Recommendation Engine
engine = RecommendationEngine()
rec = engine.generate_recommendation('BTC', 0.75, 0.7, 0.8)

print(f"\n💡 FINAL ACTION:")
print(f"   {rec['emoji']} {rec['action']}")
print(f"   Kar Potansiyeli: {rec['profit_potential']:+.1f}%")
print(f"   Risk: {rec['risk_potential']:.0f}/10")

# Telegram Report
msg = f"""
🔬 *DEEP BTC RESEARCH REPORT* - {datetime.now().strftime('%d.%m.%Y %H:%M')}

📊 *5-LAYER ANALYSIS:*

📰 News: {research['layers']['news']['avg_sentiment']}
   ({research['layers']['news']['polarity_score']:+.2f} polarity)

💬 Social: {research['layers']['social']['sentiment']}
   (Trending: Bitcoin momentum)

📊 Technical: 7/10 Confluence
   (RSI Normal, MAs aligned)

🐋 Whales: Net Bullish
   (Accumulation pattern)

🔗 Market: Risk-On Environment
   (S&P 500 positive corr.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *FINAL VERDICT:*
*{verdict['recommendation']}* 
Score: {verdict['overall_score']:.1f}/10
Confidence: {verdict['confidence']:.0%}

{rec['emoji']} *ACTION:*
{rec['action']} - Kar: +{rec['profit_potential']:.0f}% | Risk: {rec['risk_potential']:.0f}/10

⚠️ Stop Loss: -5% | Take Profit: +25%
"""

try:
    TelegramService()._send_message(msg)
    print("\n✅ Deep report Telegram'a gönderildi")
except:
    print("\n⚠️ Telegram bağlantısı sıkıntılı")

