from typing import Dict, Any, List
import json
from datetime import datetime

from config import settings

class AIEngine:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.AI_MODEL
        elif self.provider == "ollama":
            import httpx
            self.ollama_url = settings.OLLAMA_BASE_URL
            self.model = "llama2"
    
    async def analyze_root_cause(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze root cause of an incident"""
        
        prompt = self._build_root_cause_prompt(incident_data)
        
        response = await self._call_llm(prompt)
        
        # Parse response
        try:
            analysis = json.loads(response)
        except:
            analysis = {
                "root_cause": response[:500],
                "detailed_analysis": response,
                "confidence": "medium"
            }
        
        return {
            "root_cause": analysis.get("root_cause", "Analysis in progress"),
            "analysis": {
                "detailed_analysis": analysis.get("detailed_analysis", response),
                "confidence": analysis.get("confidence", "medium"),
                "contributing_factors": analysis.get("contributing_factors", []),
                "timeline": analysis.get("timeline", [])
            },
            "recommendations": analysis.get("recommendations", [
                "Monitor the situation closely",
                "Review system logs for additional context",
                "Consider scaling resources if pattern continues"
            ])
        }
    
    async def generate_monthly_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive monthly summary"""
        
        prompt = f"""Generate an executive summary for a monthly monitoring report.

Report Data:
- Month: {report_data['month']}/{report_data['year']}
- Availability: {report_data['availability_percentage']:.2f}%
- Total Incidents: {report_data['total_incidents']}
- Auto-Resolved: {report_data['auto_resolved_incidents']}
- Total Sensors: {report_data['report_data'].get('total_sensors', 0)}

Provide:
1. Executive summary (2-3 paragraphs in Portuguese)
2. Key insights (3-5 bullet points)
3. Recommendations for next month (3-5 items)

Format as JSON with keys: summary, insights, recommendations"""
        
        response = await self._call_llm(prompt)
        
        try:
            result = json.loads(response)
        except:
            result = {
                "summary": f"Durante {report_data['month']}/{report_data['year']}, o sistema manteve {report_data['availability_percentage']:.2f}% de disponibilidade com {report_data['total_incidents']} incidentes registrados.",
                "insights": [
                    f"{report_data['auto_resolved_incidents']} incidentes foram resolvidos automaticamente",
                    "Sistema operando dentro dos parâmetros esperados"
                ],
                "recommendations": [
                    "Continuar monitoramento proativo",
                    "Revisar thresholds de alertas"
                ]
            }
        
        return result
    
    async def detect_anomaly(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect anomalies in metric patterns"""
        
        if len(metrics) < 10:
            return {"anomaly_detected": False, "confidence": "low", "reason": "Insufficient data"}
        
        values = [m['value'] for m in metrics]
        avg = sum(values) / len(values)
        
        # Simple anomaly detection (in production, use more sophisticated methods)
        anomalies = []
        for i, m in enumerate(metrics):
            if abs(m['value'] - avg) > avg * 0.5:  # 50% deviation
                anomalies.append({
                    "timestamp": m.get('timestamp'),
                    "value": m['value'],
                    "deviation": abs(m['value'] - avg)
                })
        
        return {
            "anomaly_detected": len(anomalies) > 0,
            "confidence": "high" if len(anomalies) > 3 else "medium",
            "anomalies": anomalies,
            "baseline_average": avg
        }
    
    async def get_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get preventive recommendations"""
        
        prompt = f"""Based on the following monitoring context, provide preventive recommendations:

Context: {json.dumps(context, indent=2)}

Provide 3-5 actionable recommendations to prevent future incidents.
Format as JSON with key: recommendations (array of strings)"""
        
        response = await self._call_llm(prompt)
        
        try:
            result = json.loads(response)
        except:
            result = {
                "recommendations": [
                    "Review and adjust monitoring thresholds",
                    "Implement automated scaling policies",
                    "Schedule regular maintenance windows",
                    "Enhance backup and recovery procedures"
                ]
            }
        
        return result
    
    def _build_root_cause_prompt(self, incident_data: Dict[str, Any]) -> str:
        """Build prompt for root cause analysis"""
        
        prompt = f"""Analyze the following monitoring incident and provide root cause analysis:

Incident Details:
- Server: {incident_data['server_hostname']}
- Sensor: {incident_data['sensor_name']} ({incident_data['sensor_type']})
- Current Value: {incident_data.get('current_value')}
- Critical Threshold: {incident_data.get('threshold_critical')}
- Warning Threshold: {incident_data.get('threshold_warning')}
- Remediation Attempted: {incident_data['remediation_attempted']}
- Remediation Successful: {incident_data.get('remediation_successful')}

Recent Metrics (last hour):
{json.dumps(incident_data['recent_metrics'][:10], indent=2)}

Provide analysis in JSON format with:
- root_cause: Brief description of the root cause
- detailed_analysis: Detailed explanation
- confidence: low/medium/high
- contributing_factors: Array of contributing factors
- recommendations: Array of recommended actions
- timeline: Array of key events leading to the incident

Focus on actionable insights."""
        
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM provider"""
        
        if self.provider == "openai":
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert system administrator and AIOps analyst. Provide concise, actionable insights."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"AI analysis unavailable: {str(e)}"
        
        elif self.provider == "ollama":
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.ollama_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=60.0
                    )
                    if response.status_code == 200:
                        return response.json()['response']
                    else:
                        return "AI analysis unavailable"
            except Exception as e:
                return f"AI analysis unavailable: {str(e)}"
        
        return "AI provider not configured"
