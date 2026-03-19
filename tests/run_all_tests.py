"""
FASE 11 — Relatório Final: Coruja Monitor v3.0
Executa todos os testes e gera relatório de produção readiness.
Uso: python tests/run_all_tests.py
"""
import subprocess
import sys
import time
import json
from datetime import datetime

SUITES = [
    ("E2E Pipeline",         "tests/e2e/test_full_pipeline.py"),
    ("HTTP Sensor",          "tests/sensors/test_http_sensor.py"),
    ("Integration API",      "tests/integration/test_api_frontend_flow.py"),
    ("Redis Streams",        "tests/stream/test_redis_streams.py"),
    ("AI Pipeline",          "tests/ai/test_pipeline_realistic.py"),
    ("Alert Engine",         "tests/alerts/test_intelligent_alerts.py"),
    ("Event Processor",      "tests/test_event_processor.py"),
    ("Alert Engine (unit)",  "tests/test_alert_engine.py"),
    ("AI Agents (unit)",     "tests/test_ai_agents.py"),
    ("Topology Engine",      "tests/test_topology_engine.py"),
    ("Dependency Engine",    "tests/test_dependency_engine.py"),
]

CHAOS_SUITE = ("Chaos Engineering", "chaos/chaos_runner.py")


def run_pytest(path: str) -> dict:
    start = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", path, "-v", "--tb=short", "--no-header", "-q"],
        capture_output=True, text=True, timeout=120
    )
    elapsed = (time.monotonic() - start) * 1000

    # Parse pytest output
    passed = failed = errors = 0
    for line in result.stdout.splitlines():
        if " passed" in line:
            try:
                passed = int(line.strip().split()[0])
            except Exception:
                pass
        if " failed" in line:
            try:
                failed = int([x for x in line.strip().split() if x.isdigit()][0])
            except Exception:
                pass
        if " error" in line.lower():
            errors += 1

    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "elapsed_ms": round(elapsed, 0),
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
    }


def run_chaos() -> dict:
    start = time.monotonic()
    try:
        sys.path.insert(0, ".")
        from chaos.chaos_runner import ChaosRunner
        runner = ChaosRunner()
        results = runner.run_all()
        elapsed = (time.monotonic() - start) * 1000

        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)

        return {
            "passed": passed,
            "failed": failed,
            "errors": 0,
            "elapsed_ms": round(elapsed, 0),
            "returncode": 0 if failed == 0 else 1,
            "details": [str(r) for r in results],
        }
    except Exception as e:
        return {"passed": 0, "failed": 0, "errors": 1, "elapsed_ms": 0,
                "returncode": 1, "error": str(e)}


def classify(results: list) -> str:
    total_failed = sum(r["result"]["failed"] + r["result"]["errors"] for r in results)
    total_passed = sum(r["result"]["passed"] for r in results)
    critical_failed = any(
        r["result"]["failed"] > 0
        for r in results
        if r["suite"] in ("E2E Pipeline", "Alert Engine", "AI Pipeline")
    )

    if total_failed == 0 and total_passed > 0:
        return "✅ PRODUÇÃO READY"
    elif critical_failed:
        return "🔴 NÃO PRONTO — Falhas em componentes críticos"
    elif total_failed <= 3:
        return "⚠️  PRODUÇÃO COM RISCO — Falhas menores detectadas"
    else:
        return "🔴 NÃO PRONTO — Muitas falhas"


def main():
    print(f"\n{'='*60}")
    print(f"  CORUJA MONITOR v3.0 — RELATÓRIO DE VALIDAÇÃO")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    all_results = []

    for suite_name, path in SUITES:
        print(f"▶ {suite_name}...", end=" ", flush=True)
        try:
            r = run_pytest(path)
        except subprocess.TimeoutExpired:
            r = {"passed": 0, "failed": 0, "errors": 1, "elapsed_ms": 120000,
                 "returncode": 1, "stdout": "TIMEOUT"}
        except Exception as e:
            r = {"passed": 0, "failed": 0, "errors": 1, "elapsed_ms": 0,
                 "returncode": 1, "stdout": str(e)}

        status = "✅" if r["returncode"] == 0 else "❌"
        print(f"{status} {r['passed']}P/{r['failed']}F/{r['errors']}E ({r['elapsed_ms']:.0f}ms)")
        all_results.append({"suite": suite_name, "result": r})

    # Chaos
    print(f"▶ Chaos Engineering...", end=" ", flush=True)
    chaos_r = run_chaos()
    status = "✅" if chaos_r["returncode"] == 0 else "❌"
    print(f"{status} {chaos_r['passed']}P/{chaos_r['failed']}F ({chaos_r['elapsed_ms']:.0f}ms)")
    all_results.append({"suite": "Chaos Engineering", "result": chaos_r})

    # Summary
    total_passed = sum(r["result"]["passed"] for r in all_results)
    total_failed = sum(r["result"]["failed"] for r in all_results)
    total_errors = sum(r["result"]["errors"] for r in all_results)

    verdict = classify(all_results)

    print(f"\n{'='*60}")
    print(f"  RESULTADO FINAL")
    print(f"{'='*60}")
    print(f"  Testes passando : {total_passed}")
    print(f"  Testes falhando : {total_failed}")
    print(f"  Erros           : {total_errors}")
    print(f"\n  VEREDICTO: {verdict}")
    print(f"{'='*60}\n")

    # Falhas detalhadas
    for r in all_results:
        if r["result"]["failed"] > 0 or r["result"]["errors"] > 0:
            print(f"\n--- {r['suite']} (FALHAS) ---")
            print(r["result"].get("stdout", "")[-1000:])

    return 0 if total_failed == 0 and total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
