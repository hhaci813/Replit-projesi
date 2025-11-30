# 🤖 AKILLI YATIRIM ASİSTANI - PROJE DOKÜMANTASYONU

## Proje Özeti
**Yapay Zeka tabanlı yatırım yönetim sistemi** - Tamamen Türkçe, kapsamlı portföy yönetimi, teknik analiz, risk metrikleri ve makine öğrenmesi ile kendi kendini geliştiren sistem.

## MEVCUT DURUMU (AŞAMA 7 - ULTIMATE)

### ✅ Tamamlanan Özellikler:
1. **CLI Sistem** (main.py)
   - Portföy yönetimi
   - Gelişmiş teknik analiz (RSI, MACD, Bollinger Bands)
   - Risk metrikleri hesaplama
   - Backtesting sistemi
   - Fiyat tahminleme (ML)
   - Korelasyon analizi
   - Teknik desenleri tanıma
   - Excel export
   - Portföy optimizasyonu
   - Uyarı sistemi
   - Haber analizi (NewsAPI ready)
   - Temettü takibi
   - Ekonomik takvim

2. **Web Dashboard** (app.py)
   - Flask web arayüzü
   - Portföy görüntüleme
   - Yatırım ekleme/silme
   - Real-time güncelleme (5s interval)
   - REST API endpoints

3. **AI Tavsiye Sistemi** (tavsiye.py)
   - Gerçek-zamanlı pazar analizi
   - RSI & MACD hesaplama
   - Otomatik AL/SAT/TUT/BEKLE tavsiyeleri
   - 7 günlük ML öngörüsü
   - Dengeli portföy önerisi
   - Risk yönetimi kuralları

4. **Cloud Backup Sistemi** (cloud_backup.py)
   - Yerel tarihli backuplar
   - GitHub senkronizasyonu
   - CSV export
   - Manifest dosyaları

5. **Broker API Entegrasyonu** (broker_api.py)
   - Alpaca API (Hisse senedi trading)
   - Binance API (Kripto trading)
   - AL/SAT emri verme hazırlanmış

6. **Kalıcı Depolama**
   - veriler.json - Ana veri dosyası
   - backup_*.json - Tarihli backuplar
   - portfoy_kayit.csv - CSV export
   - veri_raporu_*.json - İstatistik raporları

## AKTIF WORKFLOWS

1. **Run Learning System** (main.py)
   - İnteraktif CLI menüsü
   - Her işlemden sonra otomatik kayıt
   - Durumu: RUNNING ✅

2. **Web Dashboard** (app.py)
   - Flask sunucusu Port 5000
   - Web arayüzü
   - Durumu: RUNNING ✅

## KULLANICı TERCİHLERİ

- **Dil:** Türkçe (Tamamen)
- **Veri Kaydı:** Kalıcı - Hiçbir şey silinmesin
- **Backup:** Otomatik (JSON + CSV + GitHub)
- **Pazar Analizi:** Gerçek-zaman Yahoo Finance & CoinGecko
- **Teknik Analiz:** RSI, MACD, Bollinger Bands, Trend detection
- **ML Modeli:** Kendi kendini öğrenen ve optimize eden
- **İnvestment Advisor:** AI destekli tavsiyeler

## YÜKLÜ PAKETLER

```
- flask (Web framework)
- flask-cors (CORS support)
- yfinance (Stock data)
- pandas (Data analysis)
- numpy (Numerical computing)
- scikit-learn (Machine learning)
- matplotlib (Charting)
- openpyxl (Excel export)
- requests (HTTP requests)
- newsapi (News API)
- textblob (NLP/Sentiment)
```

## SIRA YAPILACAKLAR (VARSA)

### Priority 1 - API Keys
- [ ] ALPACA_API_KEY (Broker API'yi aktifleştirmek için)
- [ ] BINANCE_API_KEY (Kripto trading için)
- [ ] NEWSAPI_API_KEY (Gerçek haberler için)

### Priority 2 - İnceleme & Optimizasyon
- [ ] Broker API'yi CLI sisteme entegre etme
- [ ] Cloud backup'ı otomatik scheduler'la çalıştırma
- [ ] Web Dashboard CSS/UX iyileştirmesi
- [ ] Multi-user/authentication sistemi

### Priority 3 - Yeni Özellikler
- [ ] Options trading (Black-Scholes)
- [ ] Robo-advisor
- [ ] Social sentiment analizi
- [ ] Portfolio rebalancing
- [ ] Tax planning reports

## ÖNEMLI DOSYALAR

| Dosya | Amaç |
|-------|------|
| main.py | CLI ana sistem |
| app.py | Web Dashboard (Flask) |
| tavsiye.py | AI Tavsiye sistemi |
| cloud_backup.py | Yedekleme modülü |
| broker_api.py | Broker API'ları |
| veriler.json | Ana veri deposu |
| portfoy_kayit.csv | CSV export |
| tavsiye_raporu.json | Son tavsiye raporu |

## HIZLI BAŞLANGAÇ

### CLI Sistemi:
```bash
# Terminal menüsünü açmak için
python main.py
```

**Menü Seçenekleri:**
- 1-3: Portföy yönetimi
- 4-6: Teknik analiz
- 7-9: Backtesting & Tahmini
- 10-12: Grafikler & Export
- 13-16: Uyarılar & Diğer
- 18: Verileri Göster
- 17: Çıkış (Güvenli kayıt)

### Web Dashboard:
```
URL: http://localhost:5000
- Portföy tablosu
- Yatırım ekleme formu
- Real-time güncelleme
```

### Tavsiye Alımı:
```bash
python tavsiye.py
```

## TEKNIK NOTLAR

- **Portföy Verisi:** JSON formatında saklanıyor - insan tarafından okunabilir
- **Backup Strategy:** Tarihli klasörlerde depolanan otomatik backuplar
- **API Rate Limits:** Yahoo Finance & CoinGecko - limite tabi
- **ML Model:** İşlemler ve sonuçlarından öğreniyor
- **Risk Metrikleri:** Sharpe, Sortino, Max Drawdown hesaplamaları
- **Diversifikasyon:** Min 5 sembol önerişi
- **Zarar Durdurma:** %5 rule otomatik kontrol

## GÜVENLİK NOTLARI

⚠️ **API Keys:**
- Alpaca/Binance keys gerçek trading için gerekli
- Paper trading modu varsayılan (Hayali para)
- Sekretler environment variables olarak depolanacak

⚠️ **Veri Gizliliği:**
- veriler.json yerel cihazda tutulur
- GitHub backup için şifreleme önerilir
- Hassas bilgileri paylaşmayın

## İLETİŞİM

- **Sistem Dili:** Türkçe (Tamamı)
- **Komut Format:** Doğal Türkçe cümleler
- **Çıktı:** Renkli, emoji kullanılan, anlaşılır

---

**Sistem Durumu:** ✅ PRODUCTION READY
**Son Güncellenme:** 30 Kasım 2025
**Geliştirme Aşaması:** 7/7 ULTIMATE
