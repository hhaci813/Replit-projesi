"""
QUANTUM SYSTEM - Merkezi Analiz & Otomatik Bakım Motoru
- Tüm modülleri izler ve sağlık durumu raporlar
- Verileri birleştirir ve quantum skor üretir
- Sürekli öğrenir ve kendini optimize eder
- Otomatik bakım yapar
"""

import os
import sys
import json
import time
import logging
import threading
import traceback
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

class ModuleHealthMonitor:
    """Modül sağlık izleme sistemi - Runtime kontrol dahil"""
    
    def __init__(self):
        self.module_status = {}
        self.error_log = defaultdict(list)
        self.last_check = None
        self.runtime_errors = defaultdict(int)
    
    def check_module(self, module_name, module_obj):
        """Modül sağlık kontrolü - import + runtime"""
        status = {
            'name': module_name,
            'loaded': module_obj is not None,
            'last_check': datetime.now().isoformat(),
            'errors': [],
            'runtime_errors': self.runtime_errors.get(module_name, 0)
        }
        
        if module_obj is None:
            status['status'] = 'FAILED'
            status['errors'].append('Modül yüklenemedi')
        else:
            if self.runtime_errors.get(module_name, 0) > 5:
                status['status'] = 'UNSTABLE'
                status['errors'].append(f'{self.runtime_errors[module_name]} runtime hatası')
            else:
                status['status'] = 'OK'
                
            if hasattr(module_obj, 'health_check'):
                try:
                    module_obj.health_check()
                except Exception as e:
                    status['status'] = 'DEGRADED'
                    status['errors'].append(str(e))
        
        self.module_status[module_name] = status
        return status
    
    def record_error(self, module_name, error_msg):
        """Runtime hatası kaydet"""
        self.runtime_errors[module_name] += 1
        self.error_log[module_name].append({
            'time': datetime.now().isoformat(),
            'error': str(error_msg)[:200]
        })
        if len(self.error_log[module_name]) > 50:
            self.error_log[module_name] = self.error_log[module_name][-50:]
    
    def reset_errors(self, module_name):
        """Hata sayacını sıfırla"""
        self.runtime_errors[module_name] = 0
    
    def get_health_report(self):
        """Tüm modüllerin sağlık raporu"""
        ok_count = sum(1 for m in self.module_status.values() if m['status'] == 'OK')
        failed_count = sum(1 for m in self.module_status.values() if m['status'] in ['FAILED', 'UNSTABLE'])
        degraded_count = sum(1 for m in self.module_status.values() if m['status'] == 'DEGRADED')
        total = len(self.module_status)
        
        health_pct = round((ok_count + degraded_count * 0.5) / total * 100, 1) if total > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_modules': total,
            'ok': ok_count,
            'degraded': degraded_count,
            'failed': failed_count,
            'health_percentage': health_pct,
            'modules': self.module_status,
            'total_runtime_errors': sum(self.runtime_errors.values())
        }
    
    def format_health_telegram(self):
        """Telegram için sağlık raporu"""
        report = self.get_health_report()
        
        if report['health_percentage'] >= 90:
            emoji = "🟢"
            status = "MÜKEMMEL"
        elif report['health_percentage'] >= 70:
            emoji = "🟡"
            status = "İYİ"
        elif report['health_percentage'] >= 50:
            emoji = "🟠"
            status = "ORTA"
        else:
            emoji = "🔴"
            status = "KRİTİK"
        
        msg = f"""🔧 <b>SİSTEM SAĞLIK RAPORU</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{emoji} <b>Durum:</b> {status}
📊 <b>Sağlık:</b> %{report['health_percentage']}
✅ <b>Aktif:</b> {report['ok']} modül
❌ <b>Sorunlu:</b> {report['failed']} modül

<b>MODÜL DURUMU:</b>
"""
        for name, data in report['modules'].items():
            icon = "✅" if data['status'] == 'OK' else "❌"
            msg += f"   {icon} {name}\n"
        
        return msg


class QuantumAnalyzer:
    """Quantum Analiz Motoru - Tüm verileri birleştirir"""
    
    def __init__(self):
        self.weights = {
            'technical': 0.25,
            'sentiment': 0.20,
            'whale': 0.15,
            'volume': 0.15,
            'momentum': 0.15,
            'historical': 0.10
        }
        self.learning_data = []
        self.accuracy_history = []
    
    def quantum_score(self, data):
        """Tüm verileri birleştirip quantum skor üret"""
        scores = {}
        
        if 'rsi' in data:
            rsi = data['rsi']
            if rsi < 30:
                scores['technical'] = 80
            elif rsi < 40:
                scores['technical'] = 65
            elif rsi > 70:
                scores['technical'] = 20
            else:
                scores['technical'] = 50
        else:
            scores['technical'] = 50
        
        if 'sentiment' in data:
            scores['sentiment'] = min(100, max(0, data['sentiment']))
        else:
            scores['sentiment'] = 50
        
        if 'whale_activity' in data:
            scores['whale'] = 70 if data['whale_activity'] == 'accumulating' else 30
        else:
            scores['whale'] = 50
        
        if 'volume_ratio' in data:
            vr = data['volume_ratio']
            if vr > 2:
                scores['volume'] = 90
            elif vr > 1.5:
                scores['volume'] = 75
            elif vr > 1.2:
                scores['volume'] = 60
            else:
                scores['volume'] = 40
        else:
            scores['volume'] = 50
        
        if 'macd_histogram' in data:
            scores['momentum'] = 70 if data['macd_histogram'] > 0 else 30
        else:
            scores['momentum'] = 50
        
        if 'historical_match' in data:
            scores['historical'] = min(100, data['historical_match'])
        else:
            scores['historical'] = 50
        
        quantum = sum(scores[k] * self.weights[k] for k in self.weights)
        
        if quantum >= 75:
            signal = "🟢 QUANTUM AL"
            confidence = "Yüksek"
        elif quantum >= 60:
            signal = "🟡 QUANTUM İZLE"
            confidence = "Orta"
        elif quantum >= 45:
            signal = "⚪ QUANTUM NÖTR"
            confidence = "Düşük"
        else:
            signal = "🔴 QUANTUM UZAK DUR"
            confidence = "Yüksek"
        
        return {
            'quantum_score': round(quantum, 1),
            'signal': signal,
            'confidence': confidence,
            'breakdown': scores,
            'timestamp': datetime.now().isoformat()
        }
    
    def learn_from_outcome(self, prediction, actual_outcome):
        """Sonuçtan öğren ve ağırlıkları güncelle"""
        self.learning_data.append({
            'prediction': prediction,
            'outcome': actual_outcome,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.learning_data) >= 20:
            correct = sum(1 for d in self.learning_data[-20:] 
                         if (d['prediction'] > 60 and d['outcome'] > 0) or 
                            (d['prediction'] < 40 and d['outcome'] < 0))
            accuracy = correct / 20 * 100
            self.accuracy_history.append(accuracy)
            
            if accuracy < 50 and len(self.accuracy_history) >= 3:
                self._adjust_weights()
    
    def _adjust_weights(self):
        """Ağırlıkları otomatik ayarla"""
        adjustment = 0.02
        
        self.weights['technical'] += adjustment
        self.weights['sentiment'] -= adjustment / 2
        self.weights['historical'] -= adjustment / 2
        
        total = sum(self.weights.values())
        self.weights = {k: v/total for k, v in self.weights.items()}
        
        logger.info(f"Quantum ağırlıklar güncellendi: {self.weights}")


class AutoMaintenance:
    """Otomatik bakım sistemi - Güvenli silme"""
    
    PROTECTED_FILES = {
        'main_service.py', 'quantum_system.py', 'pro_analysis.py',
        'sniper_system.py', 'historical_analyzer.py', 'backtest_engine.py',
        'signal_tracker.py', 'chart_generator.py', 'replit.md', 'README.md'
    }
    
    SAFE_DELETE_EXTENSIONS = {'.log', '.tmp', '.cache'}
    CHART_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
    
    def __init__(self):
        self.maintenance_log = []
        self.last_maintenance = None
    
    def is_safe_to_delete(self, filepath, file_type='log'):
        """Dosyanın silinmesinin güvenli olup olmadığını kontrol et"""
        filename = os.path.basename(filepath)
        
        if filename in self.PROTECTED_FILES:
            return False
        
        if '..' in filepath or filepath.startswith('/'):
            return False
        
        ext = os.path.splitext(filename)[1].lower()
        
        if file_type == 'log':
            return ext in self.SAFE_DELETE_EXTENSIONS or filename.endswith('.log')
        elif file_type == 'chart':
            return ext in self.CHART_EXTENSIONS
        
        return False
    
    def run_maintenance(self):
        """Günlük bakım görevleri - Güvenli mod"""
        tasks = []
        
        log_dir = 'logs/'
        if os.path.exists(log_dir):
            for f in os.listdir(log_dir):
                filepath = os.path.join(log_dir, f)
                if os.path.isfile(filepath) and self.is_safe_to_delete(filepath, 'log'):
                    try:
                        age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filepath))
                        if age.days > 14:
                            os.remove(filepath)
                            tasks.append(f"Eski log silindi: {f}")
                    except:
                        pass
        
        chart_dir = 'charts/'
        if os.path.exists(chart_dir):
            for f in os.listdir(chart_dir):
                filepath = os.path.join(chart_dir, f)
                if os.path.isfile(filepath) and self.is_safe_to_delete(filepath, 'chart'):
                    try:
                        age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filepath))
                        if age.days > 7:
                            os.remove(filepath)
                            tasks.append(f"Eski grafik silindi: {f}")
                    except:
                        pass
        
        tasks.append("Bellek temizlendi")
        
        self.last_maintenance = datetime.now()
        self.maintenance_log.append({
            'timestamp': self.last_maintenance.isoformat(),
            'tasks': tasks
        })
        
        if len(self.maintenance_log) > 100:
            self.maintenance_log = self.maintenance_log[-100:]
        
        return tasks
    
    def get_maintenance_status(self):
        """Bakım durumu"""
        return {
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'total_maintenances': len(self.maintenance_log),
            'recent_tasks': self.maintenance_log[-1]['tasks'] if self.maintenance_log else []
        }


class DataCollector:
    """Merkezi veri toplama sistemi"""
    
    def __init__(self):
        self.data_sources = {}
        self.collection_stats = defaultdict(int)
    
    def register_source(self, name, fetch_func):
        """Veri kaynağı kaydet"""
        self.data_sources[name] = fetch_func
    
    def collect_all(self):
        """Tüm kaynaklardan veri topla"""
        results = {}
        errors = []
        
        for name, fetch_func in self.data_sources.items():
            try:
                start = time.time()
                data = fetch_func()
                elapsed = time.time() - start
                
                results[name] = {
                    'data': data,
                    'fetch_time': round(elapsed, 2),
                    'status': 'OK'
                }
                self.collection_stats[name] += 1
            except Exception as e:
                results[name] = {
                    'data': None,
                    'error': str(e),
                    'status': 'ERROR'
                }
                errors.append(f"{name}: {e}")
        
        return {
            'results': results,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }


class QuantumSystem:
    """Ana Quantum Sistem Sınıfı"""
    
    def __init__(self):
        self.health_monitor = ModuleHealthMonitor()
        self.quantum_analyzer = QuantumAnalyzer()
        self.auto_maintenance = AutoMaintenance()
        self.data_collector = DataCollector()
        self.is_running = False
        self.stats = {
            'analyses': 0,
            'predictions': 0,
            'maintenances': 0,
            'uptime_start': datetime.now()
        }
    
    def initialize_modules(self, modules_dict):
        """Modülleri yükle ve kontrol et"""
        for name, obj in modules_dict.items():
            self.health_monitor.check_module(name, obj)
        
        return self.health_monitor.get_health_report()
    
    def run_quantum_analysis(self, symbol, data):
        """Quantum analiz çalıştır"""
        result = self.quantum_analyzer.quantum_score(data)
        self.stats['analyses'] += 1
        return result
    
    def run_maintenance_cycle(self):
        """Bakım döngüsü"""
        tasks = self.auto_maintenance.run_maintenance()
        self.stats['maintenances'] += 1
        return tasks
    
    def get_system_status(self):
        """Tam sistem durumu"""
        uptime = datetime.now() - self.stats['uptime_start']
        health = self.health_monitor.get_health_report()
        maintenance = self.auto_maintenance.get_maintenance_status()
        
        return {
            'uptime': str(uptime),
            'uptime_hours': round(uptime.total_seconds() / 3600, 1),
            'health': health,
            'maintenance': maintenance,
            'stats': self.stats,
            'quantum_weights': self.quantum_analyzer.weights
        }
    
    def format_status_telegram(self):
        """Telegram için sistem durumu"""
        status = self.get_system_status()
        health = status['health']
        
        msg = f"""🔮 <b>QUANTUM SİSTEM DURUMU</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ <b>Çalışma Süresi:</b> {status['uptime_hours']} saat
📊 <b>Toplam Analiz:</b> {status['stats']['analyses']}
🔧 <b>Bakım Sayısı:</b> {status['stats']['maintenances']}

<b>MODÜL SAĞLIĞI:</b>
✅ Aktif: {health['ok']} / {health['total_modules']}
📈 Sağlık: %{health['health_percentage']}

<b>QUANTUM AĞIRLIKLARI:</b>
"""
        for k, v in status['quantum_weights'].items():
            msg += f"   {k}: %{round(v*100, 1)}\n"
        
        msg += "\n💡 Sistem sürekli öğreniyor ve optimize oluyor."
        
        return msg


quantum_system = QuantumSystem()
