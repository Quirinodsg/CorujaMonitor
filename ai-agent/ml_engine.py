"""
AIOps Machine Learning Engine
Previsão de capacidade, detecção de anomalias e recomendações preventivas
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MLEngine:
    """Motor de Machine Learning para AIOps"""
    
    def __init__(self):
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.capacity_predictor = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def detect_anomalies(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detecta anomalias em métricas usando Isolation Forest
        
        Args:
            metrics: Lista de métricas com timestamp e valor
            
        Returns:
            Lista de anomalias detectadas
        """
        try:
            if len(metrics) < 10:
                logger.warning("Dados insuficientes para detecção de anomalias")
                return []
            
            # Preparar dados
            df = pd.DataFrame(metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Features: valor, hora do dia, dia da semana
            df['hour'] = df['timestamp'].dt.hour
            df['dayofweek'] = df['timestamp'].dt.dayofweek
            
            X = df[['value', 'hour', 'dayofweek']].values
            
            # Normalizar
            X_scaled = self.scaler.fit_transform(X)
            
            # Detectar anomalias
            predictions = self.anomaly_detector.fit_predict(X_scaled)
            
            # Retornar anomalias (prediction == -1)
            anomalies = []
            for idx, pred in enumerate(predictions):
                if pred == -1:
                    anomalies.append({
                        'timestamp': df.iloc[idx]['timestamp'].isoformat(),
                        'value': float(df.iloc[idx]['value']),
                        'expected_range': self._calculate_expected_range(df, idx),
                        'severity': self._calculate_anomaly_severity(df, idx),
                        'confidence': 0.85
                    })
            
            logger.info(f"Detectadas {len(anomalies)} anomalias em {len(metrics)} métricas")
            return anomalies
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalias: {e}")
            return []
    
    def predict_capacity(self, metrics: List[Dict[str, Any]], days_ahead: int = 30) -> Dict[str, Any]:
        """
        Prevê capacidade futura usando regressão
        
        Args:
            metrics: Histórico de métricas
            days_ahead: Dias para prever
            
        Returns:
            Previsão de capacidade e alertas
        """
        try:
            if len(metrics) < 30:
                logger.warning("Dados insuficientes para previsão de capacidade")
                return {
                    'status': 'insufficient_data',
                    'message': 'Necessário pelo menos 30 dias de histórico'
                }
            
            # Preparar dados
            df = pd.DataFrame(metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Features temporais
            df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()).dt.days
            df['hour'] = df['timestamp'].dt.hour
            df['dayofweek'] = df['timestamp'].dt.dayofweek
            
            # Treinar modelo
            X = df[['days_since_start', 'hour', 'dayofweek']].values
            y = df['value'].values
            
            self.capacity_predictor.fit(X, y)
            
            # Prever futuro
            last_day = df['days_since_start'].max()
            future_days = np.arange(last_day + 1, last_day + days_ahead + 1)
            
            # Prever para cada hora do dia (média)
            predictions = []
            for day in future_days:
                day_predictions = []
                for hour in range(24):
                    for dow in range(7):
                        pred = self.capacity_predictor.predict([[day, hour, dow]])[0]
                        day_predictions.append(pred)
                predictions.append(np.mean(day_predictions))
            
            # Calcular tendência
            current_avg = df['value'].tail(7).mean()
            future_avg = np.mean(predictions[-7:])
            growth_rate = ((future_avg - current_avg) / current_avg) * 100
            
            # Calcular quando atingirá limites
            threshold_warning = 80
            threshold_critical = 95
            
            days_to_warning = self._calculate_days_to_threshold(
                predictions, threshold_warning
            )
            days_to_critical = self._calculate_days_to_threshold(
                predictions, threshold_critical
            )
            
            # Gerar recomendações
            recommendations = self._generate_capacity_recommendations(
                current_avg, future_avg, growth_rate, days_to_warning, days_to_critical
            )
            
            return {
                'status': 'success',
                'current_usage': float(current_avg),
                'predicted_usage': float(future_avg),
                'growth_rate': float(growth_rate),
                'days_to_warning': days_to_warning,
                'days_to_critical': days_to_critical,
                'predictions': [float(p) for p in predictions],
                'recommendations': recommendations,
                'confidence': 0.82
            }
            
        except Exception as e:
            logger.error(f"Erro na previsão de capacidade: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def calculate_baseline(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula baseline dinâmico para métricas
        
        Args:
            metrics: Histórico de métricas
            
        Returns:
            Baseline com média, desvio padrão e limites
        """
        try:
            if len(metrics) < 7:
                return None
            
            df = pd.DataFrame(metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Calcular por hora do dia
            df['hour'] = df['timestamp'].dt.hour
            hourly_baseline = df.groupby('hour')['value'].agg(['mean', 'std']).to_dict()
            
            # Baseline geral
            mean_value = df['value'].mean()
            std_value = df['value'].std()
            
            return {
                'mean': float(mean_value),
                'std': float(std_value),
                'upper_bound': float(mean_value + 2 * std_value),
                'lower_bound': float(mean_value - 2 * std_value),
                'hourly_baseline': {
                    int(hour): {
                        'mean': float(stats['mean']),
                        'std': float(stats['std'])
                    }
                    for hour, stats in hourly_baseline.items()
                },
                'confidence': 0.90
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular baseline: {e}")
            return None
    
    def generate_preventive_recommendations(
        self, 
        server_metrics: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Gera recomendações preventivas baseadas em análise de métricas
        
        Args:
            server_metrics: Métricas por tipo (cpu, memory, disk)
            
        Returns:
            Lista de recomendações preventivas
        """
        recommendations = []
        
        try:
            # Analisar CPU
            if 'cpu' in server_metrics:
                cpu_metrics = server_metrics['cpu']
                if len(cpu_metrics) >= 24:
                    df = pd.DataFrame(cpu_metrics)
                    avg_cpu = df['value'].mean()
                    max_cpu = df['value'].max()
                    
                    if avg_cpu > 70:
                        recommendations.append({
                            'type': 'capacity',
                            'severity': 'warning' if avg_cpu < 85 else 'critical',
                            'resource': 'CPU',
                            'current_usage': float(avg_cpu),
                            'message': f'CPU média em {avg_cpu:.1f}%. Considere adicionar mais núcleos.',
                            'action': 'scale_up_cpu',
                            'priority': 'high' if avg_cpu > 85 else 'medium'
                        })
            
            # Analisar Memória
            if 'memory' in server_metrics:
                mem_metrics = server_metrics['memory']
                if len(mem_metrics) >= 24:
                    df = pd.DataFrame(mem_metrics)
                    avg_mem = df['value'].mean()
                    
                    if avg_mem > 75:
                        recommendations.append({
                            'type': 'capacity',
                            'severity': 'warning' if avg_mem < 90 else 'critical',
                            'resource': 'Memory',
                            'current_usage': float(avg_mem),
                            'message': f'Memória média em {avg_mem:.1f}%. Considere adicionar mais RAM.',
                            'action': 'scale_up_memory',
                            'priority': 'high' if avg_mem > 90 else 'medium'
                        })
            
            # Analisar Disco
            if 'disk' in server_metrics:
                disk_metrics = server_metrics['disk']
                if len(disk_metrics) >= 7:
                    df = pd.DataFrame(disk_metrics)
                    current_disk = df['value'].iloc[-1]
                    
                    if current_disk > 80:
                        recommendations.append({
                            'type': 'capacity',
                            'severity': 'critical' if current_disk > 90 else 'warning',
                            'resource': 'Disk',
                            'current_usage': float(current_disk),
                            'message': f'Disco em {current_disk:.1f}%. Limpeza ou expansão necessária.',
                            'action': 'cleanup_or_expand_disk',
                            'priority': 'critical' if current_disk > 90 else 'high'
                        })
            
            logger.info(f"Geradas {len(recommendations)} recomendações preventivas")
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            return []
    
    def _calculate_expected_range(self, df: pd.DataFrame, idx: int) -> Dict[str, float]:
        """Calcula range esperado para um ponto"""
        window = df['value'].iloc[max(0, idx-10):idx]
        if len(window) > 0:
            mean = window.mean()
            std = window.std()
            return {
                'min': float(mean - 2 * std),
                'max': float(mean + 2 * std)
            }
        return {'min': 0, 'max': 100}
    
    def _calculate_anomaly_severity(self, df: pd.DataFrame, idx: int) -> str:
        """Calcula severidade da anomalia"""
        value = df.iloc[idx]['value']
        window = df['value'].iloc[max(0, idx-10):idx]
        if len(window) > 0:
            mean = window.mean()
            std = window.std()
            z_score = abs((value - mean) / std) if std > 0 else 0
            
            if z_score > 3:
                return 'critical'
            elif z_score > 2:
                return 'warning'
        return 'info'
    
    def _calculate_days_to_threshold(self, predictions: List[float], threshold: float) -> Optional[int]:
        """Calcula dias até atingir threshold"""
        for day, pred in enumerate(predictions):
            if pred >= threshold:
                return day + 1
        return None
    
    def _generate_capacity_recommendations(
        self,
        current: float,
        future: float,
        growth_rate: float,
        days_to_warning: Optional[int],
        days_to_critical: Optional[int]
    ) -> List[str]:
        """Gera recomendações baseadas em previsão"""
        recommendations = []
        
        if growth_rate > 10:
            recommendations.append(
                f"⚠️ Crescimento acelerado de {growth_rate:.1f}% detectado. "
                "Planeje expansão de capacidade."
            )
        
        if days_to_warning and days_to_warning < 30:
            recommendations.append(
                f"🔔 Limite de aviso será atingido em ~{days_to_warning} dias. "
                "Ação preventiva recomendada."
            )
        
        if days_to_critical and days_to_critical < 15:
            recommendations.append(
                f"🚨 Limite crítico será atingido em ~{days_to_critical} dias. "
                "Ação imediata necessária!"
            )
        
        if not recommendations:
            recommendations.append(
                "✅ Capacidade adequada para os próximos 30 dias."
            )
        
        return recommendations
