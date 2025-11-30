"""3D Grafikler - Plotly ile İnteraktif Visualizasyon"""
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import json

class Grafik3D:
    @staticmethod
    def portfoy_3d_gorsel():
        """3D Portföy visualizasyonu"""
        print("\n📊 3D PORTFÖY GÖRÜNÜMÜ OLUŞTURULUYOR...\n")
        
        # Örnek veri
        semboller = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'BTC-USD', 'ETH-USD']
        fiyatlar = np.random.uniform(50, 200, len(semboller))
        adetler = np.random.uniform(1, 100, len(semboller))
        getiri = np.random.uniform(-20, 50, len(semboller))
        
        # 3D Scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=fiyatlar,
            y=adetler,
            z=getiri,
            mode='markers+text',
            text=semboller,
            textposition="top center",
            marker=dict(
                size=10,
                color=getiri,  # Renklendir
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Getiri %")
            )
        )])
        
        fig.update_layout(
            title="3D Portföy Haritası",
            scene=dict(
                xaxis_title="Fiyat ($)",
                yaxis_title="Adet",
                zaxis_title="Getiri (%)"
            ),
            height=700,
            width=900
        )
        
        # HTML'ye kaydet
        fig.write_html("portfoy_3d.html")
        print("✅ 3D Portföy: portfoy_3d.html oluşturuldu")
        
        return "portfoy_3d.html"
    
    @staticmethod
    def fiyat_yuzey_3d():
        """3D Fiyat yüzeyi"""
        print("📊 3D FİYAT YÜZEYİ OLUŞTURULUYOR...\n")
        
        # Zaman ve sembol Grid'i
        gunler = 30
        sembol_sayisi = 7
        
        X = np.arange(0, gunler)
        Y = np.arange(0, sembol_sayisi)
        X, Y = np.meshgrid(X, Y)
        
        # Fiyat yüzeyi (sinüs dalgası + gürültü)
        Z = 100 + 20*np.sin(X/5) + 10*np.cos(Y/2) + np.random.randn(sembol_sayisi, gunler)*5
        
        fig = go.Figure(data=[go.Surface(
            x=X,
            y=Y,
            z=Z,
            colorscale='Reds'
        )])
        
        fig.update_layout(
            title="30 Günlük Fiyat Hareketi (3D Yüzey)",
            scene=dict(
                xaxis_title="Gün",
                yaxis_title="Sembol",
                zaxis_title="Fiyat ($)"
            ),
            height=700
        )
        
        fig.write_html("fiyat_3d_yuzey.html")
        print("✅ 3D Yüzey: fiyat_3d_yuzey.html oluşturuldu")
        
        return "fiyat_3d_yuzey.html"
    
    @staticmethod
    def risk_getiri_3d():
        """Risk-Getiri 3D analizi"""
        print("📊 RİSK-GETİRİ 3D ANALİZİ OLUŞTURULUYOR...\n")
        
        # Portföy simülasyonu
        np.random.seed(42)
        n_portfolios = 100
        
        risks = np.random.uniform(5, 30, n_portfolios)
        returns = np.random.uniform(-10, 50, n_portfolios)
        sharpe = returns / (risks + 1)
        
        fig = go.Figure(data=[go.Scatter3d(
            x=risks,
            y=returns,
            z=sharpe,
            mode='markers',
            marker=dict(
                size=6,
                color=sharpe,
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio")
            ),
            text=[f"Risk: {r:.1f}%<br>Return: {ret:.1f}%<br>Sharpe: {s:.2f}" 
                  for r, ret, s in zip(risks, returns, sharpe)],
            hoverinfo="text"
        )])
        
        fig.update_layout(
            title="Risk-Getiri-Sharpe 3D Analizi",
            scene=dict(
                xaxis_title="Risk (Volatilite %)",
                yaxis_title="Beklenen Getiri (%)",
                zaxis_title="Sharpe Ratio"
            ),
            height=700
        )
        
        fig.write_html("risk_getiri_3d.html")
        print("✅ Risk-Getiri: risk_getiri_3d.html oluşturuldu")
        
        return "risk_getiri_3d.html"
    
    @staticmethod
    def korelasyon_3d():
        """Semboller arası korelasyon 3D"""
        print("📊 KORELASYON MATRİSİ 3D GÖRÜNÜMÜ OLUŞTURULUYOR...\n")
        
        semboller = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        korelasyon = np.random.uniform(-1, 1, (len(semboller), len(semboller)))
        np.fill_diagonal(korelasyon, 1.0)
        
        fig = go.Figure(data=[go.Heatmap(
            z=korelasyon,
            x=semboller,
            y=semboller,
            colorscale='RdBu',
            zmid=0,
            text=np.round(korelasyon, 2),
            texttemplate='%{text:.2f}',
            textfont={"size": 12},
            colorbar=dict(title="Korelasyon")
        )])
        
        fig.update_layout(
            title="Sembol Korelasyon Matrisi",
            height=600,
            width=700
        )
        
        fig.write_html("korelasyon_3d.html")
        print("✅ Korelasyon: korelasyon_3d.html oluşturuldu")
        
        return "korelasyon_3d.html"
    
    @staticmethod
    def grafikleri_uret():
        """Tüm 3D grafikleri üret"""
        print("\n" + "="*60)
        print("🎨 3D GRAFİKLER OLUŞTURULUYOR")
        print("="*60)
        
        grafikler = {
            "Portföy 3D": Grafik3D.portfoy_3d_gorsel(),
            "Fiyat Yüzeyi": Grafik3D.fiyat_yuzey_3d(),
            "Risk-Getiri": Grafik3D.risk_getiri_3d(),
            "Korelasyon": Grafik3D.korelasyon_3d(),
        }
        
        print("\n" + "="*60)
        print("✅ TÜM 3D GRAFİKLER HAZIR!")
        print("="*60)
        print("\n📁 Oluşturulan Dosyalar:")
        for ad, dosya in grafikler.items():
            print(f"   📊 {ad}: {dosya}")
        
        return grafikler

if __name__ == "__main__":
    Grafik3D.grafikleri_uret()
