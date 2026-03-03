"""
AIOps Engine - Advanced AI Operations
Implements: Anomaly Detection, Event Correlation, Root Cause Analysis, Action Plans
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json


class AIOpsEngine:
    """
    Advanced AIOps Engine following industry best practices:
    - Anomaly Detection (Statistical + ML-based)
    - Event Correlation (Temporal + Spatial)
    - Root Cause Analysis (RCA)
    - Automated Action Plans
    """
    
    def __init__(self):
        self.anomaly_threshold = 2.5  # Standard deviations
        self.correlation_window = 300  # 5 minutes in seconds
        self.min_samples_for_baseline = 20
    
    async def detect_anomalies(
        self, 
        metrics: List[Dict[str, Any]], 
        sensor_type: str
    ) -> Dict[str, Any]:
        """
        Detect anomalies using multiple methods:
        1. Statistical (Z-score)
        2. Moving Average
        3. Rate of Change
        """
        if len(metrics) < self.min_samples_for_baseline:
            return {
                "anomaly_detected": False,
                "confidence": 0.0,
                "method": "insufficient_data",
                "message": f"Necessário pelo menos {self.min_samples_for_baseline} amostras"
            }
        
        values = [m['value'] for m in metrics]
        timestamps = [m.get('timestamp', datetime.now()) for m in metrics]
        
        # Statistical Anomaly Detection (Z-score)
        statistical_anomalies = self._detect_statistical_anomalies(values)
        
        # Moving Average Anomaly Detection
        ma_anomalies = self._detect_moving_average_anomalies(values)
        
        # Rate of Change Anomaly Detection
        roc_anomalies = self._detect_rate_of_change_anomalies(values, timestamps)
        
        # Combine results
        all_anomalies = statistical_anomalies + ma_anomalies + roc_anomalies
        
        if not all_anomalies:
            return {
                "anomaly_detected": False,
                "confidence": 0.95,
                "method": "multi_method",
                "baseline": {
                    "mean": statistics.mean(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values)
                }
            }
        
        # Calculate confidence based on multiple detections
        confidence = min(len(all_anomalies) / len(values) * 2, 1.0)
        
        return {
            "anomaly_detected": True,
            "confidence": confidence,
            "method": "multi_method",
            "anomalies": all_anomalies[:10],  # Top 10
            "total_anomalies": len(all_anomalies),
            "severity": self._calculate_anomaly_severity(all_anomalies, values),
            "baseline": {
                "mean": statistics.mean(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0
            },
            "recommendation": self._get_anomaly_recommendation(sensor_type, all_anomalies)
        }
    
    def _detect_statistical_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Z-score based anomaly detection"""
        if len(values) < 2:
            return []
        
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        if std_dev == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / std_dev)
            if z_score > self.anomaly_threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "z_score": z_score,
                    "method": "statistical",
                    "deviation_percent": ((value - mean) / mean * 100) if mean != 0 else 0
                })
        
        return anomalies

    
    def _detect_moving_average_anomalies(
        self, 
        values: List[float], 
        window: int = 5
    ) -> List[Dict[str, Any]]:
        """Moving average based anomaly detection"""
        if len(values) < window:
            return []
        
        anomalies = []
        for i in range(window, len(values)):
            window_values = values[i-window:i]
            ma = statistics.mean(window_values)
            std = statistics.stdev(window_values) if len(window_values) > 1 else 0
            
            if std > 0:
                deviation = abs(values[i] - ma) / std
                if deviation > 2.0:
                    anomalies.append({
                        "index": i,
                        "value": values[i],
                        "moving_average": ma,
                        "deviation": deviation,
                        "method": "moving_average"
                    })
        
        return anomalies
    
    def _detect_rate_of_change_anomalies(
        self, 
        values: List[float],
        timestamps: List[datetime]
    ) -> List[Dict[str, Any]]:
        """Rate of change anomaly detection"""
        if len(values) < 2:
            return []
        
        anomalies = []
        for i in range(1, len(values)):
            rate_of_change = abs(values[i] - values[i-1])
            
            # Calculate time delta
            if isinstance(timestamps[i], datetime) and isinstance(timestamps[i-1], datetime):
                time_delta = (timestamps[i] - timestamps[i-1]).total_seconds()
            else:
                time_delta = 60  # Default 1 minute
            
            if time_delta > 0:
                rate_per_second = rate_of_change / time_delta
                
                # Detect sudden spikes (>20% change in short time)
                if values[i-1] != 0:
                    percent_change = (rate_of_change / values[i-1]) * 100
                    if percent_change > 20 and time_delta < 120:  # 20% in 2 minutes
                        anomalies.append({
                            "index": i,
                            "value": values[i],
                            "previous_value": values[i-1],
                            "rate_of_change": rate_of_change,
                            "percent_change": percent_change,
                            "method": "rate_of_change"
                        })
        
        return anomalies

    
    def _calculate_anomaly_severity(
        self, 
        anomalies: List[Dict[str, Any]], 
        all_values: List[float]
    ) -> str:
        """Calculate overall severity of anomalies"""
        if not anomalies:
            return "none"
        
        anomaly_ratio = len(anomalies) / len(all_values)
        
        if anomaly_ratio > 0.5:
            return "critical"
        elif anomaly_ratio > 0.3:
            return "high"
        elif anomaly_ratio > 0.1:
            return "medium"
        else:
            return "low"
    
    def _get_anomaly_recommendation(
        self, 
        sensor_type: str, 
        anomalies: List[Dict[str, Any]]
    ) -> str:
        """Get recommendation based on anomaly type"""
        recommendations = {
            "cpu": "Investigar processos com alto consumo de CPU. Considerar escalonamento horizontal.",
            "memory": "Verificar memory leaks. Analisar processos com crescimento de memória.",
            "disk": "Limpar arquivos temporários. Implementar rotação de logs.",
            "network": "Analisar tráfego de rede. Verificar possíveis ataques ou transferências anormais.",
            "service": "Verificar logs de aplicação. Analisar dependências do serviço."
        }
        
        return recommendations.get(sensor_type, "Investigar causa raiz da anomalia detectada.")
    
    async def correlate_events(
        self, 
        incidents: List[Dict[str, Any]],
        time_window_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Correlate events using:
        1. Temporal Correlation (events close in time)
        2. Spatial Correlation (events on same server/network)
        3. Causal Correlation (one event causes another)
        """
        if len(incidents) < 2:
            return {
                "correlated": False,
                "groups": [],
                "message": "Insufficient incidents for correlation"
            }
        
        # Sort by timestamp
        sorted_incidents = sorted(
            incidents, 
            key=lambda x: x.get('created_at', datetime.now())
        )
        
        # Temporal Correlation
        temporal_groups = self._correlate_temporal(sorted_incidents, time_window_seconds)
        
        # Spatial Correlation
        spatial_groups = self._correlate_spatial(sorted_incidents)
        
        # Merge correlations
        merged_groups = self._merge_correlation_groups(temporal_groups, spatial_groups)
        
        return {
            "correlated": len(merged_groups) > 0,
            "total_groups": len(merged_groups),
            "groups": merged_groups,
            "analysis": self._analyze_correlation_patterns(merged_groups)
        }

    
    def _correlate_temporal(
        self, 
        incidents: List[Dict[str, Any]], 
        window_seconds: int
    ) -> List[List[Dict[str, Any]]]:
        """Group incidents that occur close in time"""
        groups = []
        current_group = []
        
        for i, incident in enumerate(incidents):
            if not current_group:
                current_group.append(incident)
                continue
            
            # Check time difference with last incident in group
            last_time = current_group[-1].get('created_at', datetime.now())
            current_time = incident.get('created_at', datetime.now())
            
            if isinstance(last_time, datetime) and isinstance(current_time, datetime):
                time_diff = (current_time - last_time).total_seconds()
            else:
                time_diff = 0
            
            if time_diff <= window_seconds:
                current_group.append(incident)
            else:
                if len(current_group) > 1:
                    groups.append(current_group)
                current_group = [incident]
        
        if len(current_group) > 1:
            groups.append(current_group)
        
        return groups
    
    def _correlate_spatial(
        self, 
        incidents: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group incidents on same server or related infrastructure"""
        server_groups = defaultdict(list)
        
        for incident in incidents:
            server_id = incident.get('server_id') or incident.get('server_hostname', 'unknown')
            server_groups[server_id].append(incident)
        
        # Return only groups with multiple incidents
        return [group for group in server_groups.values() if len(group) > 1]
    
    def _merge_correlation_groups(
        self, 
        temporal: List[List[Dict[str, Any]]], 
        spatial: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Merge temporal and spatial correlations"""
        merged = []
        
        for temp_group in temporal:
            incident_ids = {inc.get('id') for inc in temp_group}
            
            # Find matching spatial group
            matching_spatial = None
            for spat_group in spatial:
                spat_ids = {inc.get('id') for inc in spat_group}
                if incident_ids & spat_ids:  # Intersection
                    matching_spatial = spat_group
                    break
            
            merged.append({
                "correlation_type": "temporal_spatial" if matching_spatial else "temporal",
                "incident_count": len(temp_group),
                "incidents": temp_group,
                "time_span_seconds": self._calculate_time_span(temp_group),
                "affected_servers": list(set(inc.get('server_hostname', 'unknown') for inc in temp_group)),
                "severity": self._calculate_group_severity(temp_group)
            })
        
        return merged

    
    def _calculate_time_span(self, incidents: List[Dict[str, Any]]) -> float:
        """Calculate time span of incident group"""
        if len(incidents) < 2:
            return 0.0
        
        times = [inc.get('created_at', datetime.now()) for inc in incidents]
        times = [t for t in times if isinstance(t, datetime)]
        
        if len(times) < 2:
            return 0.0
        
        return (max(times) - min(times)).total_seconds()
    
    def _calculate_group_severity(self, incidents: List[Dict[str, Any]]) -> str:
        """Calculate overall severity of incident group"""
        severities = [inc.get('severity', 'warning') for inc in incidents]
        
        if 'critical' in severities:
            return 'critical'
        elif 'warning' in severities:
            return 'warning'
        else:
            return 'info'
    
    def _analyze_correlation_patterns(self, groups: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in correlated events"""
        if not groups:
            return {}
        
        total_incidents = sum(g['incident_count'] for g in groups)
        affected_servers = set()
        for g in groups:
            affected_servers.update(g['affected_servers'])
        
        return {
            "total_correlated_incidents": total_incidents,
            "total_affected_servers": len(affected_servers),
            "largest_group_size": max(g['incident_count'] for g in groups),
            "pattern": self._identify_pattern(groups)
        }
    
    def _identify_pattern(self, groups: List[Dict[str, Any]]) -> str:
        """Identify common patterns in incident groups"""
        if not groups:
            return "none"
        
        # Check if multiple servers affected simultaneously
        multi_server_groups = [g for g in groups if len(g['affected_servers']) > 1]
        if len(multi_server_groups) > len(groups) / 2:
            return "infrastructure_wide"
        
        # Check if cascading failures
        if len(groups) > 1:
            time_spans = [g['time_span_seconds'] for g in groups]
            if max(time_spans) > 600:  # 10 minutes
                return "cascading_failure"
        
        return "isolated_incidents"

    
    async def analyze_root_cause(
        self, 
        incident: Dict[str, Any],
        related_incidents: List[Dict[str, Any]],
        metrics_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Root Cause Analysis using:
        1. Symptom Analysis
        2. Timeline Reconstruction
        3. Dependency Analysis
        4. Pattern Matching
        """
        
        # Analyze symptoms
        symptoms = self._analyze_symptoms(incident, metrics_history)
        
        # Reconstruct timeline
        timeline = self._reconstruct_timeline(incident, related_incidents, metrics_history)
        
        # Identify dependencies
        dependencies = self._analyze_dependencies(incident, related_incidents)
        
        # Match known patterns
        pattern_match = self._match_known_patterns(incident, symptoms)
        
        # Determine root cause
        root_cause = self._determine_root_cause(
            incident, symptoms, timeline, dependencies, pattern_match
        )
        
        return {
            "root_cause": root_cause,
            "confidence": self._calculate_rca_confidence(symptoms, pattern_match),
            "symptoms": symptoms,
            "timeline": timeline,
            "dependencies": dependencies,
            "pattern_match": pattern_match,
            "contributing_factors": self._identify_contributing_factors(
                symptoms, timeline, dependencies
            )
        }
    
    def _analyze_symptoms(
        self, 
        incident: Dict[str, Any], 
        metrics: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze symptoms from metrics"""
        symptoms = []
        
        sensor_type = incident.get('sensor_type', 'unknown')
        current_value = incident.get('current_value', 0)
        
        # Primary symptom
        symptoms.append({
            "type": "primary",
            "description": f"{sensor_type} at {current_value}",
            "severity": incident.get('severity', 'warning'),
            "timestamp": incident.get('created_at', datetime.now())
        })
        
        # Analyze metric trends
        if len(metrics) >= 5:
            values = [m['value'] for m in metrics[-10:]]
            
            # Check for gradual increase
            if all(values[i] <= values[i+1] for i in range(len(values)-1)):
                symptoms.append({
                    "type": "trend",
                    "description": "Gradual increase detected",
                    "severity": "warning"
                })
            
            # Check for sudden spike
            if len(values) >= 2:
                last_change = abs(values[-1] - values[-2])
                avg_change = statistics.mean([abs(values[i] - values[i-1]) for i in range(1, len(values))])
                
                if last_change > avg_change * 3:
                    symptoms.append({
                        "type": "spike",
                        "description": "Sudden spike detected",
                        "severity": "critical"
                    })
        
        return symptoms

    
    def _reconstruct_timeline(
        self,
        incident: Dict[str, Any],
        related_incidents: List[Dict[str, Any]],
        metrics: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Reconstruct timeline of events"""
        timeline = []
        
        # Add metric changes
        if len(metrics) >= 2:
            for i in range(1, min(len(metrics), 10)):
                if abs(metrics[i]['value'] - metrics[i-1]['value']) > metrics[i-1]['value'] * 0.1:
                    timeline.append({
                        "timestamp": metrics[i].get('timestamp', datetime.now()),
                        "event": "metric_change",
                        "description": f"Value changed from {metrics[i-1]['value']:.1f} to {metrics[i]['value']:.1f}",
                        "type": "metric"
                    })
        
        # Add related incidents
        for rel_inc in related_incidents[:5]:
            timeline.append({
                "timestamp": rel_inc.get('created_at', datetime.now()),
                "event": "related_incident",
                "description": f"{rel_inc.get('sensor_name', 'Unknown')} - {rel_inc.get('severity', 'unknown')}",
                "type": "incident"
            })
        
        # Add current incident
        timeline.append({
            "timestamp": incident.get('created_at', datetime.now()),
            "event": "current_incident",
            "description": f"{incident.get('sensor_name', 'Unknown')} triggered",
            "type": "incident"
        })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        return timeline[-10:]  # Last 10 events
    
    def _analyze_dependencies(
        self,
        incident: Dict[str, Any],
        related_incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze dependencies between incidents"""
        
        # Group by server
        same_server = [
            inc for inc in related_incidents 
            if inc.get('server_id') == incident.get('server_id')
        ]
        
        # Group by sensor type
        same_type = [
            inc for inc in related_incidents 
            if inc.get('sensor_type') == incident.get('sensor_type')
        ]
        
        return {
            "same_server_incidents": len(same_server),
            "same_type_incidents": len(same_type),
            "dependency_level": "high" if len(same_server) > 2 else "medium" if len(same_server) > 0 else "low"
        }

    
    def _match_known_patterns(
        self,
        incident: Dict[str, Any],
        symptoms: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Match against known failure patterns"""
        
        sensor_type = incident.get('sensor_type', 'unknown')
        severity = incident.get('severity', 'warning')
        
        patterns = {
            "memory_leak": {
                "conditions": ["sensor_type == 'memory'", "gradual_increase", "high_severity"],
                "confidence": 0.85,
                "description": "Memory leak pattern detected"
            },
            "cpu_spike": {
                "conditions": ["sensor_type == 'cpu'", "sudden_spike", "critical"],
                "confidence": 0.90,
                "description": "CPU spike pattern detected"
            },
            "disk_full": {
                "conditions": ["sensor_type == 'disk'", "gradual_increase"],
                "confidence": 0.95,
                "description": "Disk filling pattern detected"
            },
            "service_crash": {
                "conditions": ["sensor_type == 'service'", "sudden_change"],
                "confidence": 0.80,
                "description": "Service crash pattern detected"
            },
            "network_congestion": {
                "conditions": ["sensor_type == 'network'", "high_values"],
                "confidence": 0.75,
                "description": "Network congestion pattern detected"
            }
        }
        
        # Check symptoms for pattern indicators
        has_gradual_increase = any(s['type'] == 'trend' for s in symptoms)
        has_spike = any(s['type'] == 'spike' for s in symptoms)
        
        matched_pattern = None
        for pattern_name, pattern_data in patterns.items():
            if sensor_type in pattern_name or (
                sensor_type == 'memory' and has_gradual_increase and pattern_name == 'memory_leak'
            ) or (
                sensor_type == 'cpu' and has_spike and pattern_name == 'cpu_spike'
            ):
                matched_pattern = {
                    "name": pattern_name,
                    "confidence": pattern_data['confidence'],
                    "description": pattern_data['description']
                }
                break
        
        return matched_pattern or {"name": "unknown", "confidence": 0.5, "description": "No known pattern matched"}

    
    def _determine_root_cause(
        self,
        incident: Dict[str, Any],
        symptoms: List[Dict[str, Any]],
        timeline: List[Dict[str, Any]],
        dependencies: Dict[str, Any],
        pattern_match: Dict[str, Any]
    ) -> str:
        """Determine the root cause based on all analysis"""
        
        sensor_type = incident.get('sensor_type', 'unknown')
        
        root_causes = {
            "cpu": {
                "memory_leak": "Processo com memory leak causando alto uso de CPU",
                "cpu_spike": "Processo travado ou malware consumindo CPU",
                "default": "Alto consumo de CPU por processo desconhecido"
            },
            "memory": {
                "memory_leak": "Memory leak em aplicação - memória não sendo liberada",
                "default": "Alto consumo de memória - possível falta de recursos"
            },
            "disk": {
                "disk_full": "Disco enchendo gradualmente - logs ou arquivos temporários",
                "default": "Espaço em disco insuficiente"
            },
            "service": {
                "service_crash": "Serviço travou devido a erro de aplicação ou dependência",
                "default": "Serviço parou de responder"
            },
            "network": {
                "network_congestion": "Congestionamento de rede - tráfego excessivo",
                "default": "Problemas de conectividade de rede"
            }
        }
        
        pattern_name = pattern_match.get('name', 'default')
        sensor_causes = root_causes.get(sensor_type, {"default": "Causa raiz desconhecida"})
        
        return sensor_causes.get(pattern_name, sensor_causes.get('default'))
    
    def _calculate_rca_confidence(
        self,
        symptoms: List[Dict[str, Any]],
        pattern_match: Dict[str, Any]
    ) -> float:
        """Calculate confidence in root cause analysis"""
        
        base_confidence = pattern_match.get('confidence', 0.5)
        
        # Increase confidence with more symptoms
        symptom_bonus = min(len(symptoms) * 0.05, 0.2)
        
        return min(base_confidence + symptom_bonus, 0.95)
    
    def _identify_contributing_factors(
        self,
        symptoms: List[Dict[str, Any]],
        timeline: List[Dict[str, Any]],
        dependencies: Dict[str, Any]
    ) -> List[str]:
        """Identify contributing factors"""
        factors = []
        
        if len(symptoms) > 2:
            factors.append("Múltiplos sintomas detectados indicando problema complexo")
        
        if dependencies.get('same_server_incidents', 0) > 1:
            factors.append("Múltiplos sensores afetados no mesmo servidor")
        
        if len(timeline) > 5:
            factors.append("Problema evoluiu ao longo do tempo")
        
        return factors or ["Incidente isolado sem fatores contribuintes identificados"]

    
    async def create_action_plan(
        self,
        incident: Dict[str, Any],
        root_cause_analysis: Dict[str, Any],
        correlation_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive action plan with:
        1. Immediate Actions (stop the bleeding)
        2. Short-term Actions (fix the problem)
        3. Long-term Actions (prevent recurrence)
        """
        
        sensor_type = incident.get('sensor_type', 'unknown')
        severity = incident.get('severity', 'warning')
        root_cause = root_cause_analysis.get('root_cause', '')
        
        # Generate actions based on sensor type and root cause
        immediate_actions = self._generate_immediate_actions(sensor_type, severity, incident)
        short_term_actions = self._generate_short_term_actions(sensor_type, root_cause, incident)
        long_term_actions = self._generate_long_term_actions(sensor_type, root_cause_analysis)
        
        # Add correlation-based actions
        if correlation_data and correlation_data.get('correlated'):
            immediate_actions.extend(self._generate_correlation_actions(correlation_data))
        
        return {
            "plan_id": f"AP-{incident.get('id', 'unknown')}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "incident_id": incident.get('id'),
            "severity": severity,
            "estimated_resolution_time": self._estimate_resolution_time(immediate_actions, short_term_actions),
            "immediate_actions": immediate_actions,
            "short_term_actions": short_term_actions,
            "long_term_actions": long_term_actions,
            "automation_available": self._check_automation_available(sensor_type),
            "rollback_plan": self._generate_rollback_plan(immediate_actions),
            "success_criteria": self._define_success_criteria(sensor_type, incident)
        }
    
    def _generate_immediate_actions(
        self,
        sensor_type: str,
        severity: str,
        incident: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate immediate actions to stop the bleeding"""
        
        actions_map = {
            "cpu": [
                {
                    "priority": 1,
                    "action": "Identificar processo com maior consumo de CPU",
                    "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5",
                    "automated": True,
                    "estimated_time": "1 min",
                    "risk_level": "low"
                },
                {
                    "priority": 2,
                    "action": "Verificar se processo está travado",
                    "command": "Get-Process | Where-Object {$_.Responding -eq $false}",
                    "automated": True,
                    "estimated_time": "30 sec",
                    "risk_level": "low"
                }
            ],
            "memory": [
                {
                    "priority": 1,
                    "action": "Identificar processo com maior consumo de memória",
                    "command": "Get-Process | Sort-Object WS -Descending | Select-Object -First 5",
                    "automated": True,
                    "estimated_time": "1 min",
                    "risk_level": "low"
                },
                {
                    "priority": 2,
                    "action": "Limpar cache do sistema",
                    "command": "[System.GC]::Collect()",
                    "automated": True,
                    "estimated_time": "30 sec",
                    "risk_level": "low"
                }
            ],
            "disk": [
                {
                    "priority": 1,
                    "action": "Verificar espaço disponível em disco",
                    "command": "Get-PSDrive -PSProvider FileSystem",
                    "automated": True,
                    "estimated_time": "30 sec",
                    "risk_level": "low"
                },
                {
                    "priority": 2,
                    "action": "Identificar maiores arquivos/pastas",
                    "command": "Get-ChildItem C:\\ -Recurse -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 10",
                    "automated": True,
                    "estimated_time": "2 min",
                    "risk_level": "low"
                }
            ],
            "service": [
                {
                    "priority": 1,
                    "action": f"Verificar status do serviço {incident.get('sensor_name', '')}",
                    "command": f"Get-Service -Name {incident.get('sensor_name', '').replace('service_', '')}",
                    "automated": True,
                    "estimated_time": "30 sec",
                    "risk_level": "low"
                },
                {
                    "priority": 2,
                    "action": "Tentar reiniciar o serviço",
                    "command": f"Restart-Service -Name {incident.get('sensor_name', '').replace('service_', '')}",
                    "automated": True,
                    "estimated_time": "1 min",
                    "risk_level": "medium"
                }
            ],
            "network": [
                {
                    "priority": 1,
                    "action": "Verificar conectividade de rede",
                    "command": "Test-NetConnection -ComputerName 8.8.8.8",
                    "automated": True,
                    "estimated_time": "30 sec",
                    "risk_level": "low"
                },
                {
                    "priority": 2,
                    "action": "Verificar estatísticas de rede",
                    "command": "Get-NetAdapterStatistics",
                    "automated": True,
                    "estimated_time": "30 sec",
                    "risk_level": "low"
                }
            ]
        }
        
        return actions_map.get(sensor_type, [
            {
                "priority": 1,
                "action": "Coletar informações do sistema",
                "command": "Get-ComputerInfo",
                "automated": True,
                "estimated_time": "1 min",
                "risk_level": "low"
            }
        ])

    
    def _generate_short_term_actions(
        self,
        sensor_type: str,
        root_cause: str,
        incident: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate short-term actions to fix the problem"""
        
        actions = []
        
        if "memory leak" in root_cause.lower():
            actions.append({
                "priority": 1,
                "action": "Reiniciar aplicação com memory leak",
                "automated": False,
                "estimated_time": "5 min",
                "risk_level": "medium",
                "requires_approval": True
            })
        
        if "disk" in sensor_type:
            actions.append({
                "priority": 1,
                "action": "Limpar arquivos temporários e logs antigos",
                "command": "Remove-Item $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue",
                "automated": True,
                "estimated_time": "5 min",
                "risk_level": "low"
            })
        
        if "service" in sensor_type:
            actions.append({
                "priority": 1,
                "action": "Verificar logs de erro do serviço",
                "command": f"Get-EventLog -LogName Application -Source {incident.get('sensor_name', '').replace('service_', '')} -Newest 50",
                "automated": True,
                "estimated_time": "2 min",
                "risk_level": "low"
            })
        
        # Generic action
        actions.append({
            "priority": 2,
            "action": "Documentar incidente e ações tomadas",
            "automated": False,
            "estimated_time": "10 min",
            "risk_level": "low"
        })
        
        return actions
    
    def _generate_long_term_actions(
        self,
        sensor_type: str,
        root_cause_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate long-term actions to prevent recurrence"""
        
        actions = [
            {
                "priority": 1,
                "action": "Revisar e ajustar thresholds de monitoramento",
                "automated": False,
                "estimated_time": "30 min",
                "risk_level": "low"
            },
            {
                "priority": 2,
                "action": "Implementar alertas proativos baseados em tendências",
                "automated": False,
                "estimated_time": "2 horas",
                "risk_level": "low"
            },
            {
                "priority": 3,
                "action": "Criar runbook para este tipo de incidente",
                "automated": False,
                "estimated_time": "1 hora",
                "risk_level": "low"
            }
        ]
        
        # Sensor-specific long-term actions
        if sensor_type == "memory":
            actions.append({
                "priority": 2,
                "action": "Implementar monitoramento de memory leaks",
                "automated": False,
                "estimated_time": "4 horas",
                "risk_level": "low"
            })
        
        if sensor_type == "disk":
            actions.append({
                "priority": 2,
                "action": "Implementar rotação automática de logs",
                "automated": False,
                "estimated_time": "2 horas",
                "risk_level": "low"
            })
        
        return actions

    
    def _generate_correlation_actions(
        self,
        correlation_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actions based on correlated events"""
        
        pattern = correlation_data.get('analysis', {}).get('pattern', 'none')
        
        if pattern == "infrastructure_wide":
            return [{
                "priority": 1,
                "action": "Verificar infraestrutura compartilhada (rede, storage, hypervisor)",
                "automated": False,
                "estimated_time": "10 min",
                "risk_level": "low"
            }]
        
        if pattern == "cascading_failure":
            return [{
                "priority": 1,
                "action": "Identificar e isolar componente causador da falha em cascata",
                "automated": False,
                "estimated_time": "15 min",
                "risk_level": "medium"
            }]
        
        return []
    
    def _estimate_resolution_time(
        self,
        immediate_actions: List[Dict[str, Any]],
        short_term_actions: List[Dict[str, Any]]
    ) -> str:
        """Estimate total resolution time"""
        
        # Parse time strings and sum
        total_minutes = 0
        
        for action in immediate_actions + short_term_actions:
            time_str = action.get('estimated_time', '0 min')
            if 'min' in time_str:
                total_minutes += int(time_str.split()[0])
            elif 'hour' in time_str or 'hora' in time_str:
                total_minutes += int(time_str.split()[0]) * 60
        
        if total_minutes < 60:
            return f"{total_minutes} minutos"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}min"
    
    def _check_automation_available(self, sensor_type: str) -> bool:
        """Check if automation is available for this sensor type"""
        automated_types = ['cpu', 'memory', 'disk', 'service']
        return sensor_type in automated_types
    
    def _generate_rollback_plan(
        self,
        immediate_actions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate rollback plan in case actions fail"""
        
        return [
            {
                "step": 1,
                "action": "Reverter alterações feitas",
                "description": "Desfazer comandos executados se possível"
            },
            {
                "step": 2,
                "action": "Restaurar configuração anterior",
                "description": "Usar backup de configuração se disponível"
            },
            {
                "step": 3,
                "action": "Escalar para equipe de suporte",
                "description": "Contatar especialista se problema persistir"
            }
        ]
    
    def _define_success_criteria(
        self,
        sensor_type: str,
        incident: Dict[str, Any]
    ) -> List[str]:
        """Define success criteria for resolution"""
        
        threshold_warning = incident.get('threshold_warning', 80)
        threshold_critical = incident.get('threshold_critical', 95)
        
        return [
            f"Valor do sensor abaixo de {threshold_warning}% (threshold de aviso)",
            "Sem novos alertas por pelo menos 15 minutos",
            "Métricas estáveis e dentro da baseline",
            "Causa raiz documentada e ações preventivas definidas"
        ]
