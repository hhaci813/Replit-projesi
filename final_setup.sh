#!/bin/bash

echo "🧹 CLEANUP & FINAL SETUP"

# Remove duplicate/temp files
rm -f telegram_btc_*.py quick_telegram_send.py main_telegram_bot.py telegram_bot_*.py telegram_webhook*.py app_integration.py

# Create README
cat > BTC_COMMAND_README.md << 'DOC'
# 📱 Telegram /btc Komutu - HAZIR!

## 🎯 Sistem Nedir?

Telegram'da `/btc` yazınca sistem:

1. **BTCTurk 337+ Kripto'yu Analiz Eder**
   - Yükselen olanları bulur
   - STRONG_BUY seçer
   - Kar potansiyelini gösterir

2. **Hisse Senetlerini Tarar**
   - AAPL, MSFT, GOOGL, TSLA vs
   - Teknik analiz yapıp tavsiye verir
   - Kesin AL önerileri verir

3. **Detaylı Tavsiye Verir**
   ```
   🔥 LUNA +66% → Hedef: +91% | Stop: -5%
   🔥 CVC  +20% → Hedef: +45% | Stop: -5%
   
   💻 TSLA +5.7% → Hedef: +20% | Stop: -3%
   💻 ADBE +7.4% → Hedef: +22% | Stop: -3%
   ```

## 📊 Örnek Output

```
🎯 KESIN AL ÖNERİLERİ - 05.12.2025 20:48

🔥 STRONG_BUY KRİPTO (Kesin Al):
1. LUNA +66.37% | Hedef: +25% | Stop: -5%
2. CVC +20.30% | Hedef: +25% | Stop: -5%

💻 STRONG_BUY HİSSE (Kesin Al):
1. TSLA +5.68% | Hedef: +20% | Stop: -3%
2. ADBE +7.39% | Hedef: +20% | Stop: -3%
3. CRM +11.78% | Hedef: +20% | Stop: -3%

⚠️ KURALLARI UYGULA:
✅ STRONG_BUY = Kesin al
✅ BUY = Fırsat varsa al
❌ Stop Loss: MUTLAKA koy
❌ Diversify: 5+ sembol min
```

## 🚀 KULLANIM

```
1. Telegram aç
2. Bot'a yaz: /btc
3. Kesin AL önerileri al
4. STRONG_BUY'ları işleme al
5. Stop Loss koy!
6. Hedeflere ulaşınca çık
```

## 📋 Komutlar

| Komut | Yapıyor |
|-------|---------|
| `/btc` | Kesin AL önerileri |
| `/help` | Komut listesi |
| `/portfolio` | Portföy önerisi |

## 🎊 ÖZETİ

✅ Sistem 24/7 aktif
✅ Yükselen kripto'ları otomatik bulur
✅ Yükselen hisse'leri otomatik söyler
✅ Kar/zarar potansiyelini gösterir
✅ Stop loss uyarısı verir
✅ Deep research entegre
✅ Dashboard'da grafik görüntülenir

**Telegram'da /btc yaz - Kesin AL önerileri al!** 🚀

DOC

echo "✅ Cleanup complete"
echo "✅ Documentation created"

