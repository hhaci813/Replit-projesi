"""
BTCTurk Gerçek Trade Modülü
Real trading with BTCTurk API - AL/SAT işlemleri
PostgreSQL entegrasyonu ile kalıcı veri
"""

import os
import time
import hmac
import base64
import hashlib
import requests
import json
import logging
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

ALLOWED_SYMBOLS = ['BTC', 'ETH', 'XRP', 'SOL', 'AVAX', 'DOGE', 'ADA', 'DOT', 'MATIC', 'LINK', 
                   'UNI', 'ATOM', 'FIL', 'LTC', 'TRX', 'XLM', 'ALGO', 'VET', 'NEAR', 'APE',
                   'SAND', 'MANA', 'GALA', 'AXS', 'ENJ', 'CHZ', 'SHIB', 'FLOKI', 'PEPE', 'JUV']

MAX_ORDER_TL = 50000
MIN_ORDER_TL = 50

def get_db_connection():
    """PostgreSQL bağlantısı"""
    try:
        return psycopg2.connect(os.environ.get('DATABASE_URL'))
    except Exception as e:
        logger.error(f"DB bağlantı hatası: {e}")
        return None

class BTCTurkTrader:
    """BTCTurk API ile gerçek alım/satım işlemleri"""
    
    BASE_URL = "https://api.btcturk.com"
    
    def __init__(self):
        self.api_key = os.environ.get('BTCTURK_API_KEY', '')
        self.api_secret = os.environ.get('BTCTURK_API_SECRET', '')
        self.trade_history_file = Path('trade_history.json')
        self.authorized_chat_ids = self._load_authorized_users()
        self.load_trade_history()
    
    def _load_authorized_users(self) -> list:
        """Yetkili kullanıcıları yükle"""
        main_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        if main_chat_id:
            return [int(main_chat_id)]
        return []
    
    def is_authorized(self, chat_id: int) -> bool:
        """Kullanıcı yetkili mi kontrol et"""
        return chat_id in self.authorized_chat_ids
    
    def validate_order(self, symbol: str, amount_tl: float = None, quantity: float = None) -> dict:
        """Order güvenlik kontrolü"""
        if symbol.upper() not in ALLOWED_SYMBOLS:
            return {'valid': False, 'error': f'❌ {symbol} desteklenmiyor. Desteklenen: {", ".join(ALLOWED_SYMBOLS[:10])}...'}
        
        if amount_tl:
            if amount_tl < MIN_ORDER_TL:
                return {'valid': False, 'error': f'❌ Minimum order: ₺{MIN_ORDER_TL}'}
            if amount_tl > MAX_ORDER_TL:
                return {'valid': False, 'error': f'❌ Maksimum order: ₺{MAX_ORDER_TL:,}'}
        
        if quantity and quantity <= 0:
            return {'valid': False, 'error': '❌ Geçersiz miktar'}
        
        return {'valid': True}
    
    def save_trade_to_db(self, trade_data: dict):
        """Trade'i veritabanına kaydet"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO trades (symbol, side, quantity, price, total_tl, order_type, status, order_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    trade_data.get('symbol'),
                    trade_data.get('side'),
                    trade_data.get('quantity'),
                    trade_data.get('price'),
                    trade_data.get('total_tl'),
                    trade_data.get('order_type', 'market'),
                    trade_data.get('status', 'completed'),
                    trade_data.get('order_id')
                ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Trade DB kayıt hatası: {e}")
            return False
        finally:
            conn.close()
        
    def load_trade_history(self):
        """Trade geçmişini yükle"""
        if self.trade_history_file.exists():
            with open(self.trade_history_file, 'r') as f:
                self.trade_history = json.load(f)
        else:
            self.trade_history = {'trades': [], 'stats': {'total_trades': 0, 'wins': 0, 'losses': 0}}
            
    def save_trade_history(self):
        """Trade geçmişini kaydet"""
        with open(self.trade_history_file, 'w') as f:
            json.dump(self.trade_history, f, indent=2, ensure_ascii=False)
    
    def _get_signature(self, timestamp: int) -> str:
        """API imzası oluştur"""
        message = f"{self.api_key}{timestamp}"
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_headers(self) -> dict:
        """API headers oluştur"""
        timestamp = int(time.time() * 1000)
        return {
            'X-PCK': self.api_key,
            'X-Stamp': str(timestamp),
            'X-Signature': self._get_signature(timestamp),
            'Content-Type': 'application/json'
        }
    
    def get_balance(self, asset: str = None) -> dict:
        """Bakiye sorgula"""
        try:
            resp = requests.get(
                f"{self.BASE_URL}/api/v1/users/balances",
                headers=self._get_headers(),
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json().get('data', [])
                balances = {}
                
                for item in data:
                    symbol = item.get('asset', '')
                    free = float(item.get('free', 0))
                    locked = float(item.get('locked', 0))
                    
                    if free > 0 or locked > 0:
                        balances[symbol] = {
                            'free': free,
                            'locked': locked,
                            'total': free + locked
                        }
                
                if asset:
                    return balances.get(asset.upper(), {'free': 0, 'locked': 0, 'total': 0})
                return balances
            else:
                logger.error(f"Bakiye hatası: {resp.status_code} - {resp.text}")
                return {}
        except Exception as e:
            logger.error(f"Bakiye sorgulama hatası: {e}")
            return {}
    
    def get_ticker(self, symbol: str) -> dict:
        """Güncel fiyat bilgisi"""
        try:
            resp = requests.get(
                f"{self.BASE_URL}/api/v2/ticker?pairSymbol={symbol}TRY",
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json().get('data', [])
                if data:
                    return {
                        'symbol': symbol,
                        'price': float(data[0].get('last', 0)),
                        'bid': float(data[0].get('bid', 0)),
                        'ask': float(data[0].get('ask', 0)),
                        'volume': float(data[0].get('volume', 0)),
                        'change_24h': float(data[0].get('dailyPercent', 0))
                    }
            return {}
        except Exception as e:
            logger.error(f"Ticker hatası: {e}")
            return {}
    
    def place_market_order(self, symbol: str, side: str, quantity: float = None, 
                          amount_tl: float = None) -> dict:
        """
        Market order ver
        side: 'buy' veya 'sell'
        quantity: Alınacak/satılacak miktar (coin cinsinden)
        amount_tl: Harcanacak TL miktarı (sadece alımda)
        """
        try:
            pair = f"{symbol.upper()}TRY"
            order_type = 'buy' if side.lower() == 'buy' else 'sell'
            
            ticker = self.get_ticker(symbol)
            current_price = ticker.get('price', 0)
            
            if not current_price:
                return {'success': False, 'error': 'Fiyat alınamadı'}
            
            if order_type == 'buy' and amount_tl:
                quantity = amount_tl / current_price
            
            if not quantity or quantity <= 0:
                return {'success': False, 'error': 'Geçersiz miktar'}
            
            order_data = {
                'quantity': str(round(quantity, 8)),
                'price': '0',
                'stopPrice': '0',
                'newOrderClientId': f"trade_{int(time.time())}",
                'orderMethod': 'market',
                'orderType': order_type,
                'pairSymbol': pair
            }
            
            resp = requests.post(
                f"{self.BASE_URL}/api/v1/order",
                headers=self._get_headers(),
                json=order_data,
                timeout=15
            )
            
            result = resp.json()
            
            if resp.status_code == 200 and result.get('success'):
                order_info = result.get('data', {})
                
                trade_record = {
                    'id': order_info.get('id', str(int(time.time()))),
                    'symbol': symbol.upper(),
                    'side': order_type,
                    'quantity': quantity,
                    'price': current_price,
                    'total_tl': quantity * current_price,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'completed',
                    'order_id': order_info.get('id')
                }
                
                self.trade_history['trades'].append(trade_record)
                self.trade_history['stats']['total_trades'] += 1
                self.save_trade_history()
                
                return {
                    'success': True,
                    'order_id': order_info.get('id'),
                    'symbol': symbol,
                    'side': order_type,
                    'quantity': quantity,
                    'price': current_price,
                    'total_tl': quantity * current_price,
                    'message': f"✅ {order_type.upper()} order başarılı!"
                }
            else:
                error_msg = result.get('message', 'Bilinmeyen hata')
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Order hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, 
                         price: float) -> dict:
        """Limit order ver"""
        try:
            pair = f"{symbol.upper()}TRY"
            order_type = 'buy' if side.lower() == 'buy' else 'sell'
            
            order_data = {
                'quantity': str(round(quantity, 8)),
                'price': str(round(price, 2)),
                'stopPrice': '0',
                'newOrderClientId': f"limit_{int(time.time())}",
                'orderMethod': 'limit',
                'orderType': order_type,
                'pairSymbol': pair
            }
            
            resp = requests.post(
                f"{self.BASE_URL}/api/v1/order",
                headers=self._get_headers(),
                json=order_data,
                timeout=15
            )
            
            result = resp.json()
            
            if resp.status_code == 200 and result.get('success'):
                order_info = result.get('data', {})
                
                trade_record = {
                    'id': order_info.get('id', str(int(time.time()))),
                    'symbol': symbol.upper(),
                    'side': order_type,
                    'quantity': quantity,
                    'price': price,
                    'total_tl': quantity * price,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending',
                    'order_type': 'limit',
                    'order_id': order_info.get('id')
                }
                
                self.trade_history['trades'].append(trade_record)
                self.trade_history['stats']['total_trades'] += 1
                self.save_trade_history()
                
                return {
                    'success': True,
                    'order_id': order_info.get('id'),
                    'symbol': symbol,
                    'side': order_type,
                    'quantity': quantity,
                    'price': price,
                    'total_tl': quantity * price,
                    'message': f"✅ Limit {order_type.upper()} order oluşturuldu!"
                }
            else:
                error_msg = result.get('message', 'Bilinmeyen hata')
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Limit order hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def place_stop_order(self, symbol: str, side: str, quantity: float, 
                        stop_price: float, limit_price: float = None) -> dict:
        """Stop-loss / Take-profit order"""
        try:
            pair = f"{symbol.upper()}TRY"
            order_type = 'buy' if side.lower() == 'buy' else 'sell'
            
            order_data = {
                'quantity': str(round(quantity, 8)),
                'price': str(round(limit_price or stop_price, 2)),
                'stopPrice': str(round(stop_price, 2)),
                'newOrderClientId': f"stop_{int(time.time())}",
                'orderMethod': 'stoplimit' if limit_price else 'stopmarket',
                'orderType': order_type,
                'pairSymbol': pair
            }
            
            resp = requests.post(
                f"{self.BASE_URL}/api/v1/order",
                headers=self._get_headers(),
                json=order_data,
                timeout=15
            )
            
            result = resp.json()
            
            if resp.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'order_id': result.get('data', {}).get('id'),
                    'message': f"✅ Stop order oluşturuldu @ ₺{stop_price:,.2f}"
                }
            else:
                return {'success': False, 'error': result.get('message', 'Hata')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, order_id: str) -> dict:
        """Order iptal et"""
        try:
            resp = requests.delete(
                f"{self.BASE_URL}/api/v1/order",
                headers=self._get_headers(),
                params={'id': order_id},
                timeout=10
            )
            
            if resp.status_code == 200:
                return {'success': True, 'message': f'Order {order_id} iptal edildi'}
            else:
                return {'success': False, 'error': resp.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_open_orders(self, symbol: str = None) -> list:
        """Açık orderları listele"""
        try:
            params = {}
            if symbol:
                params['pairSymbol'] = f"{symbol.upper()}TRY"
                
            resp = requests.get(
                f"{self.BASE_URL}/api/v1/openOrders",
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                asks = data.get('asks', [])
                bids = data.get('bids', [])
                return asks + bids
            return []
            
        except Exception as e:
            logger.error(f"Open orders hatası: {e}")
            return []
    
    def get_trade_stats(self) -> dict:
        """Trade istatistikleri"""
        trades = self.trade_history.get('trades', [])
        
        if not trades:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'total_profit_tl': 0
            }
        
        completed = [t for t in trades if t.get('status') == 'completed']
        buys = [t for t in completed if t.get('side') == 'buy']
        sells = [t for t in completed if t.get('side') == 'sell']
        
        total_buy = sum(t.get('total_tl', 0) for t in buys)
        total_sell = sum(t.get('total_tl', 0) for t in sells)
        
        return {
            'total_trades': len(completed),
            'buy_count': len(buys),
            'sell_count': len(sells),
            'total_buy_tl': total_buy,
            'total_sell_tl': total_sell,
            'net_pnl': total_sell - total_buy,
            'win_rate': self.trade_history['stats'].get('wins', 0) / max(len(completed), 1) * 100
        }
    
    def format_balance_message(self) -> str:
        """Bakiye mesajı formatla"""
        balances = self.get_balance()
        
        if not balances:
            return "❌ Bakiye alınamadı. API anahtarlarını kontrol edin."
        
        msg = "💰 <b>HESAP BAKİYESİ</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        total_tl = 0
        
        for asset, balance in balances.items():
            if balance['total'] > 0.00001:
                ticker = self.get_ticker(asset) if asset != 'TRY' else None
                price = ticker.get('price', 1) if ticker else 1
                value_tl = balance['total'] * price if asset != 'TRY' else balance['total']
                total_tl += value_tl
                
                msg += f"💎 <b>{asset}</b>\n"
                msg += f"   Miktar: {balance['total']:.8f}\n"
                if asset != 'TRY':
                    msg += f"   Değer: ₺{value_tl:,.2f}\n"
                msg += "\n"
        
        msg += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"📊 <b>TOPLAM DEĞER:</b> ₺{total_tl:,.2f}\n"
        
        return msg


class SignalTracker:
    """Sinyal başarı oranı takip sistemi"""
    
    def __init__(self):
        self.signals_file = Path('signals_history.json')
        self.load_signals()
    
    def load_signals(self):
        if self.signals_file.exists():
            with open(self.signals_file, 'r') as f:
                self.signals = json.load(f)
        else:
            self.signals = {'signals': [], 'stats': {}}
    
    def save_signals(self):
        with open(self.signals_file, 'w') as f:
            json.dump(self.signals, f, indent=2, ensure_ascii=False)
    
    def record_signal(self, symbol: str, signal_type: str, entry_price: float,
                     target_price: float, stop_loss: float, score: float) -> str:
        """Yeni sinyal kaydet"""
        signal_id = f"{symbol}_{int(time.time())}"
        
        signal = {
            'id': signal_id,
            'symbol': symbol,
            'type': signal_type,
            'entry_price': entry_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'score': score,
            'timestamp': datetime.now().isoformat(),
            'status': 'ACTIVE',
            'result': None,
            'exit_price': None,
            'pnl_percent': None
        }
        
        self.signals['signals'].append(signal)
        self.save_signals()
        return signal_id
    
    def update_signal(self, signal_id: str, status: str, exit_price: float = None):
        """Sinyal sonucunu güncelle"""
        for signal in self.signals['signals']:
            if signal['id'] == signal_id:
                signal['status'] = status
                if exit_price:
                    signal['exit_price'] = exit_price
                    entry = signal['entry_price']
                    if signal['type'] in ['BUY', 'STRONG_BUY']:
                        signal['pnl_percent'] = ((exit_price - entry) / entry) * 100
                    else:
                        signal['pnl_percent'] = ((entry - exit_price) / entry) * 100
                    
                    signal['result'] = 'WIN' if signal['pnl_percent'] > 0 else 'LOSS'
                break
        
        self.save_signals()
    
    def get_stats(self) -> dict:
        """Sinyal istatistikleri"""
        signals = self.signals.get('signals', [])
        
        completed = [s for s in signals if s.get('result')]
        wins = [s for s in completed if s.get('result') == 'WIN']
        losses = [s for s in completed if s.get('result') == 'LOSS']
        
        total_pnl = sum(s.get('pnl_percent', 0) for s in completed)
        
        return {
            'total_signals': len(signals),
            'active': len([s for s in signals if s.get('status') == 'ACTIVE']),
            'completed': len(completed),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / max(len(completed), 1) * 100,
            'avg_pnl': total_pnl / max(len(completed), 1),
            'total_pnl': total_pnl
        }
    
    def format_stats_message(self) -> str:
        """İstatistik mesajı"""
        stats = self.get_stats()
        
        msg = "📊 <b>SİNYAL PERFORMANSI</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        msg += f"📈 Toplam Sinyal: {stats['total_signals']}\n"
        msg += f"🟢 Aktif: {stats['active']}\n"
        msg += f"✅ Tamamlanan: {stats['completed']}\n\n"
        
        msg += f"🏆 Kazanan: {stats['wins']}\n"
        msg += f"❌ Kaybeden: {stats['losses']}\n"
        msg += f"📊 Başarı Oranı: %{stats['win_rate']:.1f}\n\n"
        
        msg += f"💰 Ortalama Kar/Zarar: %{stats['avg_pnl']:.2f}\n"
        msg += f"📈 Toplam Kar/Zarar: %{stats['total_pnl']:.2f}\n"
        
        return msg


if __name__ == "__main__":
    trader = BTCTurkTrader()
    print(trader.format_balance_message())
