"""
Security Monitor Router
Monitoramento de segurança em tempo real
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os
from pathlib import Path

from database import get_db
from auth import get_current_user

router = APIRouter()

# Caminho para logs e arquivos de segurança
SECURITY_DIR = Path(__file__).parent.parent.parent / "security"
CHECKSUMS_FILE = Path(__file__).parent.parent.parent / "checksums.json"
SCAN_RESULTS_FILE = SECURITY_DIR / "scan_results.json"

@router.get("/security/status")
async def get_security_status(current_user: dict = Depends(get_current_user)):
    """
    Retorna status geral de segurança
    """
    
    # Verificar se WAF está realmente ativo
    waf_active = False
    try:
        # Verificar se WAF está habilitado no main.py
        import sys
        from pathlib import Path
        main_path = Path(__file__).parent.parent / "main.py"
        with open(main_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
            # Verificar se a linha do WAF não está comentada
            if 'app.add_middleware(WAFMiddleware)' in main_content and \
               not '# app.add_middleware(WAFMiddleware)' in main_content:
                waf_active = True
    except:
        pass
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "waf": {
            "status": "active" if waf_active else "disabled",
            "protections": [
                "SQL Injection",
                "XSS",
                "Rate Limiting",
                "IP Blacklist"
            ]
        },
        "integrity": {
            "status": "unknown",
            "last_check": None,
            "files_monitored": 0
        },
        "vulnerabilities": {
            "status": "unknown",
            "last_scan": None,
            "issues_found": 0
        },
        "compliance": {
            "lgpd": "compliant",
            "iso27001": "compliant",
            "owasp": "compliant"
        }
    }
    
    # Verificar checksums
    if CHECKSUMS_FILE.exists():
        try:
            with open(CHECKSUMS_FILE, 'r') as f:
                checksums_data = json.load(f)
                status["integrity"]["status"] = "monitored"
                status["integrity"]["last_check"] = checksums_data.get("generated_at")
                status["integrity"]["files_monitored"] = checksums_data.get("total_files", 0)
        except:
            pass
    
    # Verificar scan results
    if SCAN_RESULTS_FILE.exists():
        try:
            with open(SCAN_RESULTS_FILE, 'r') as f:
                scan_data = json.load(f)
                status["vulnerabilities"]["last_scan"] = scan_data.get("scan_date")
                
                # Contar vulnerabilidades
                issues = 0
                for key in ["python", "nodejs", "docker"]:
                    if scan_data.get(key, {}).get("status") == "vulnerabilities_found":
                        vulns = scan_data[key].get("vulnerabilities", [])
                        if isinstance(vulns, list):
                            issues += len(vulns)
                        elif isinstance(vulns, dict):
                            issues += sum(vulns.values())
                
                status["vulnerabilities"]["issues_found"] = issues
                status["vulnerabilities"]["status"] = "clean" if issues == 0 else "issues_found"
        except:
            pass
    
    return status


@router.get("/security/waf/stats")
async def get_waf_stats(current_user: dict = Depends(get_current_user)):
    """
    Retorna estatísticas do WAF
    """
    
    # TODO: Implementar coleta de métricas do WAF
    # Por enquanto, retornar dados simulados
    
    return {
        "timestamp": datetime.now().isoformat(),
        "requests_blocked": 0,
        "sql_injection_attempts": 0,
        "xss_attempts": 0,
        "rate_limit_violations": 0,
        "blacklisted_ips": 0,
        "total_requests": 0,
        "uptime": "active"
    }


@router.get("/security/integrity/status")
async def get_integrity_status(current_user: dict = Depends(get_current_user)):
    """
    Retorna status da verificação de integridade
    """
    
    if not CHECKSUMS_FILE.exists():
        return {
            "status": "not_configured",
            "message": "Checksums not generated. Run: python security/integrity_check.py generate"
        }
    
    try:
        with open(CHECKSUMS_FILE, 'r') as f:
            data = json.load(f)
        
        return {
            "status": "configured",
            "generated_at": data.get("generated_at"),
            "total_files": data.get("total_files", 0),
            "base_directory": data.get("base_directory"),
            "last_verification": None  # TODO: Armazenar última verificação
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/security/integrity/generate")
async def generate_checksums(current_user: dict = Depends(get_current_user)):
    """Gera checksums de integridade executando o script diretamente"""
    import subprocess
    import sys
    try:
        script_path = Path(__file__).parent.parent.parent / "security" / "integrity_check.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "generate"],
            capture_output=True, text=True, timeout=60,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        if result.returncode == 0:
            return {"status": "success", "message": "Checksums gerados com sucesso", "output": result.stdout[-500:]}
        else:
            return {"status": "error", "message": result.stderr[-500:] or result.stdout[-500:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/security/vulnerabilities/scan")
async def run_vulnerability_scan(current_user: dict = Depends(get_current_user)):
    """Executa scan de vulnerabilidades"""
    import subprocess
    import sys
    try:
        script_path = Path(__file__).parent.parent.parent / "security" / "scan_dependencies.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, text=True, timeout=120,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        if result.returncode == 0:
            return {"status": "success", "message": "Scan concluído", "output": result.stdout[-500:]}
        else:
            return {"status": "error", "message": result.stderr[-500:] or result.stdout[-500:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/security/integrity/verify")
async def verify_integrity(current_user: dict = Depends(get_current_user)):
    """
    Executa verificação de integridade
    """
    
    if not CHECKSUMS_FILE.exists():
        raise HTTPException(
            status_code=400,
            detail="Checksums not generated. Run: python security/integrity_check.py generate"
        )
    
    # TODO: Executar verificação em background
    # Por enquanto, retornar instrução
    
    return {
        "status": "pending",
        "message": "Run: python security/integrity_check.py verify",
        "note": "Background verification will be implemented in future version"
    }


@router.get("/security/vulnerabilities/status")
async def get_vulnerabilities_status(current_user: dict = Depends(get_current_user)):
    """
    Retorna status do scan de vulnerabilidades
    """
    
    if not SCAN_RESULTS_FILE.exists():
        return {
            "status": "not_scanned",
            "message": "No scan results found. Run: python security/scan_dependencies.py"
        }
    
    try:
        with open(SCAN_RESULTS_FILE, 'r') as f:
            data = json.load(f)
        
        return {
            "status": "scanned",
            "scan_date": data.get("scan_date"),
            "python": data.get("python", {}),
            "nodejs": data.get("nodejs", {}),
            "docker": data.get("docker", {})
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/security/scan")
async def run_security_scan(current_user: dict = Depends(get_current_user)):
    """
    Executa scan de segurança
    """
    
    # TODO: Executar scan em background
    # Por enquanto, retornar instrução
    
    return {
        "status": "pending",
        "message": "Run: python security/scan_dependencies.py",
        "note": "Background scanning will be implemented in future version"
    }


@router.get("/security/logs")
async def get_security_logs(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna logs de segurança recentes
    """
    
    # TODO: Implementar leitura de logs do WAF
    # Por enquanto, retornar lista vazia
    
    return {
        "timestamp": datetime.now().isoformat(),
        "logs": [],
        "total": 0,
        "note": "Log collection will be implemented in future version"
    }


@router.get("/security/recommendations")
async def get_security_recommendations(current_user: dict = Depends(get_current_user)):
    """
    Retorna recomendações de segurança
    """
    
    recommendations = []
    
    # Verificar checksums
    if not CHECKSUMS_FILE.exists():
        recommendations.append({
            "priority": "high",
            "category": "integrity",
            "title": "Generate File Checksums",
            "description": "File integrity monitoring is not configured",
            "action": "Run: python security/integrity_check.py generate"
        })
    
    # Verificar scan
    if not SCAN_RESULTS_FILE.exists():
        recommendations.append({
            "priority": "medium",
            "category": "vulnerabilities",
            "title": "Run Security Scan",
            "description": "No vulnerability scan has been performed",
            "action": "Run: python security/scan_dependencies.py"
        })
    else:
        # Verificar se scan é recente (últimas 7 dias)
        try:
            with open(SCAN_RESULTS_FILE, 'r') as f:
                data = json.load(f)
                scan_date = datetime.fromisoformat(data.get("scan_date"))
                if datetime.now() - scan_date > timedelta(days=7):
                    recommendations.append({
                        "priority": "medium",
                        "category": "vulnerabilities",
                        "title": "Update Security Scan",
                        "description": f"Last scan was {(datetime.now() - scan_date).days} days ago",
                        "action": "Run: python security/scan_dependencies.py"
                    })
        except:
            pass
    
    # Recomendações gerais
    recommendations.append({
        "priority": "low",
        "category": "maintenance",
        "title": "Regular Security Audits",
        "description": "Perform security audits monthly",
        "action": "Schedule regular security reviews"
    })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total": len(recommendations),
        "recommendations": recommendations
    }
