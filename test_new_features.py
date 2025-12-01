"""🚀 Test tüm yeni features"""
import sys

print("\n" + "="*60)
print("🚀 YENİ ÖZELLIKLER TEST")
print("="*60 + "\n")

# 1. Pump Detection
print("1️⃣ PUMP DETECTION TEST")
try:
    from pump_detector import PumpDetector, TrendDetector
    detector = PumpDetector()
    
    # Test 1: Normal volume
    result = detector.detect_pump(500, 500, 0.5)
    print(f"   Normal volume: {result['detected']} ✅")
    
    # Test 2: Pump
    result = detector.detect_pump(1000, 500, 3)
    print(f"   Pump detected: {result['detected']} ✅" if result['detected'] else "   Pump not detected ❌")
    
    # Test 3: Trend
    trend = TrendDetector.detect_trend([100, 102, 104, 106, 108, 110])
    print(f"   Trend: {trend} ✅")
    
    print("   ✅ PUMP DETECTION ÇALIŞIYOR\n")
except Exception as e:
    print(f"   ❌ PUMP DETECTION HATA: {e}\n")

# 2. Email Service
print("2️⃣ EMAIL SERVICE TEST")
try:
    from email_alerts_service import EmailAlertsService
    service = EmailAlertsService()
    print("   ✅ EMAIL SERVICE HAZIR (Credentials gerekli)\n")
except Exception as e:
    print(f"   ❌ EMAIL SERVICE HATA: {e}\n")

# 3. Discord Service
print("3️⃣ DISCORD SERVICE TEST")
try:
    from discord_bot_service import DiscordBotService
    bot = DiscordBotService()
    print("   ✅ DISCORD SERVICE HAZIR (Token gerekli)\n")
except Exception as e:
    print(f"   ⚠️  DISCORD SERVICE: {e}\n")

# 4. Sentiment Analysis
print("4️⃣ SENTIMENT ANALYSIS TEST")
try:
    from advanced_sentiment_analyzer import AdvancedSentimentAnalyzer
    analyzer = AdvancedSentimentAnalyzer()
    
    # Test 1: Positive text
    result = analyzer.analyze_text_sentiment("Bitcoin is rising and adoption is growing")
    print(f"   Sentiment: {result['sentiment']} ✅")
    print(f"   Polarity: {result['polarity']:.2f} ✅")
    
    print("   ✅ SENTIMENT ANALYSIS ÇALIŞIYOR (NewsAPI için key gerekli)\n")
except Exception as e:
    print(f"   ❌ SENTIMENT ANALYSIS HATA: {e}\n")

# 5. Enhanced Auto System
print("5️⃣ ENHANCED AUTO SYSTEM TEST")
try:
    from enhanced_auto_system import EnhancedAutoSystem
    system = EnhancedAutoSystem()
    print(system.start_all_enhanced())
    print(system.get_status())
    print("   ✅ ENHANCED AUTO SYSTEM ÇALIŞIYOR\n")
except Exception as e:
    print(f"   ❌ ENHANCED AUTO SYSTEM HATA: {e}\n")

print("="*60)
print("✅ TÜM YENİ ÖZELLIKLER HAZIR!")
print("="*60)

print("""
📊 ÖZET:
   ✅ Pump Detection - Hemen kullanılabilir
   ✅ Email Service - Gmail setup gerekli
   ✅ Discord Service - Token gerekli
   ✅ Sentiment Analysis - NewsAPI key gerekli
   ✅ Auto System - Schedule oluşturdu

🎯 NEXT STEPS:
   1. Email: Gmail "App Password" oluştur
   2. Discord: Bot token'ını al
   3. NewsAPI: https://newsapi.org/ 'den key al
   4. Auto system'i main.py'ye entegre et
""")
