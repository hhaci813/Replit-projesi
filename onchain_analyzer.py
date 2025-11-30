"""On-chain Analiz - Blockchain Metrikleri"""

class OnchainAnalyzer:
    def __init__(self):
        self.blockchain_metrics = {
            "BTC": {"active_addresses": 1000000, "whale_count": 500, "circulation": 21000000},
            "ETH": {"active_addresses": 800000, "whale_count": 300, "circulation": 120000000}
        }
    
    def get_whale_activity(self, symbol):
        """Balina aktivitesi"""
        if symbol in self.blockchain_metrics:
            metrics = self.blockchain_metrics[symbol]
            return {
                "whales": metrics["whale_count"],
                "status": f"🐋 {metrics['whale_count']} balina aktif",
                "trend": "📈 Yükseliş" if metrics['whale_count'] > 400 else "📉 Düşüş"
            }
        return {"status": "Veri yok"}
    
    def get_active_addresses(self, symbol):
        """Aktif adres sayısı"""
        if symbol in self.blockchain_metrics:
            addresses = self.blockchain_metrics[symbol]["active_addresses"]
            return {
                "count": addresses,
                "status": f"👥 {addresses:,} aktif adres"
            }
        return {"status": "Veri yok"}
    
    def get_circulation(self, symbol):
        """Dolaşımdaki miktar"""
        if symbol in self.blockchain_metrics:
            circ = self.blockchain_metrics[symbol]["circulation"]
            return {
                "circulation": circ,
                "status": f"📊 Dolaşım: {circ:,}"
            }
        return {"status": "Veri yok"}
    
    def network_health(self, symbol):
        """Ağ sağlığı"""
        if symbol in self.blockchain_metrics:
            return {
                "health": "🟢 Sağlıklı",
                "score": 8.5,
                "metrics": {
                    "security": "Yüksek",
                    "activity": "Yüksek",
                    "centralization": "Düşük"
                }
            }
        return {"health": "Bilinmiyor"}
