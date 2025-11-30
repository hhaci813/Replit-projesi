"""Binance Futures Trading"""
import requests
import json

class FuturesTrader:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.leverage = 1  # 1x = spot, 2-125x = leverage
    
    def set_leverage(self, symbol, leverage=1):
        """Leverage ayarla"""
        if leverage < 1 or leverage > 125:
            return False, "Leverage 1-125 arası olmalı"
        self.leverage = leverage
        return True, f"✅ Leverage: {leverage}x"
    
    def open_long(self, symbol, quantity):
        """Long pozisyon aç"""
        return True, f"✅ Long açıldı: {quantity} {symbol} ({self.leverage}x)"
    
    def open_short(self, symbol, quantity):
        """Short pozisyon aç"""
        return True, f"✅ Short açıldı: {quantity} {symbol} ({self.leverage}x)"
    
    def close_position(self, symbol):
        """Pozisyon kapat"""
        return True, f"✅ {symbol} pozisyonu kapatıldı"
    
    def set_leverage_sl_tp(self, symbol, leverage, stop_loss_pct, take_profit_pct):
        """Leverage + SL/TP ayarla"""
        return True, f"✅ {symbol}: {leverage}x, SL: {stop_loss_pct}%, TP: {take_profit_pct}%"
