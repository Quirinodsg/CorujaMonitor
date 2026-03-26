from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.types import ASGIApp, Receive, Scope, Send
from contextlib import asynccontextmanager
import logging
import logging.config
import json
import time

# ── JSON Logging Enterprise ──────────────────────────────────────────────────
class _JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "service": "coruja-api",
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)

_handler = logging.StreamHandler()
_handler.setFormatter(_JsonFormatter())
logging.root.setLevel(logging.INFO)
logging.root.handlers = [_handler]
# ─────────────────────────────────────────────────────────────────────────────


class SlashNormalizerMiddleware:
    """
    Adiciona trailing slash APENAS nas rotas de coleção raiz (nível 3).
    Ex: /api/v1/servers → /api/v1/servers/   ✓
        /api/v1/auth/login → sem alteração    ✓ (tem sub-path)
        /api/v1/servers/123 → sem alteração   ✓ (tem ID)
    """
    # Rotas de coleção raiz que precisam de trailing slash
    _COLLECTION_ROUTES = {
        "/api/v1/servers", "/api/v1/probes", "/api/v1/sensors",
        "/api/v1/tenants", "/api/v1/incidents", "/api/v1/users",
        "/api/v1/sensor-groups", "/api/v1/reports", "/api/v1/custom-reports",
        "/api/v1/maintenance", "/api/v1/notifications", "/api/v1/knowledge-base",
        "/api/v1/ai-activities", "/api/v1/sensor-notes", "/api/v1/backup",
        "/api/v1/thresholds", "/api/v1/metrics", "/api/v1/credentials",
    }

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path in self._COLLECTION_ROUTES:
                scope = dict(scope)
                scope["path"] = path + "/"
                raw = scope.get("raw_path", path.encode())
                scope["raw_path"] = raw + b"/"
        await self.app(scope, receive, send)


class ForceCORSMiddleware:
    """
    Middleware ASGI minimalista que injeta Access-Control-Allow-Origin em TODA resposta.
    Garante CORS mesmo quando exception handlers ou outros middlewares omitem o header.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Capturar origin do request
        headers = dict(scope.get("headers", []))
        origin = headers.get(b"origin", b"*").decode("utf-8")

        # Responder preflight OPTIONS diretamente
        if scope["method"] == "OPTIONS":
            response = Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept",
                    "Access-Control-Max-Age": "86400",
                },
            )
            await response(scope, receive, send)
            return

        # Para outros métodos: interceptar send para injetar header
        async def send_with_cors(message):
            if message["type"] == "http.response.start":
                headers_list = list(message.get("headers", []))
                # Remover qualquer ACAO header existente para evitar duplicata
                headers_list = [
                    (k, v) for k, v in headers_list
                    if k.lower() not in (
                        b"access-control-allow-origin",
                        b"access-control-allow-credentials",
                    )
                ]
                headers_list.append((b"access-control-allow-origin", origin.encode()))
                message = {**message, "headers": headers_list}
            await send(message)

        await self.app(scope, receive, send_with_cors)

from database import engine, Base
from middleware.error_handler import GlobalErrorHandlerMiddleware
from routers import auth, tenants, probes, servers, sensors, metrics, incidents, reports, dashboard, probe_commands, users, sensor_notes, ai_analysis, notifications, maintenance, admin_tools, aiops, noc, noc_realtime, test_tools, knowledge_base, ai_activities, ai_config, threshold_config, seed_kb, custom_reports, backup, sensor_groups, kubernetes, kubernetes_alerts, metrics_dashboard, auth_config, credentials, mfa, security_monitor, system_reset, timescale_migration, multi_probe, probe_nodes, metrics_batch, ws_dashboard, discovery, observability, topology, aiops_v3, aiops_pipeline, internal_health, sensor_controls, service_map, audit, predictions, service_monitor, default_sensor_profiles, hyperv, hyperv_ws

# WAF desabilitado temporariamente — conflito com CORSMiddleware no Starlette
WAF_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    # Backfill do FailurePredictor com histórico do banco
    try:
        from database import SessionLocal
        from routers.predictions import backfill_predictor
        db = SessionLocal()
        try:
            backfill_predictor(db)
        finally:
            db.close()
    except Exception as e:
        import logging
        logging.getLogger("coruja.startup").warning("Backfill predictor ignorado: %s", e)
    yield
    # Shutdown

app = FastAPI(
    title="Coruja Monitor API",
    description="Enterprise monitoring platform with AIOps capabilities",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS — allow_credentials=False é obrigatório quando allow_origins=["*"]
# (browser rejeita credentials=True + wildcard origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ForceCORSMiddleware — garante Access-Control-Allow-Origin em TODA resposta,
# incluindo erros 401/403/500 onde o CORSMiddleware falha.
# Registrado por último = executa primeiro (mais externo na cadeia ASGI).
app.add_middleware(ForceCORSMiddleware)

# SlashNormalizerMiddleware — remove trailing slash das URLs antes de rotear.
# Evita 307 redirect do FastAPI que expõe hostname interno Docker ao browser.
# Registrado após ForceCORSMiddleware para ser o mais externo.
app.add_middleware(SlashNormalizerMiddleware)

# GlobalErrorHandlerMiddleware — captura exceções não tratadas, retorna JSON estruturado.
# Registrado após ForceCORSMiddleware para que CORS seja aplicado mesmo em erros 500.
app.add_middleware(GlobalErrorHandlerMiddleware)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": " | ".join(error_messages) if error_messages else "Validation error"
        }
    )

# Handler global para HTTPException — retorna JSON limpo (CORS é tratado pelo ForceCORSMiddleware)
from fastapi import HTTPException as FastAPIHTTPException

@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(mfa.router, prefix="/api/v1", tags=["MFA"])
app.include_router(auth_config.router, prefix="/api/v1", tags=["Authentication Config"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(probes.router, prefix="/api/v1/probes", tags=["Probes"])
app.include_router(servers.router, prefix="/api/v1/servers", tags=["Servers"])
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["Sensors"])
app.include_router(sensor_notes.router, prefix="/api/v1/sensor-notes", tags=["Sensor Notes"])
app.include_router(ai_analysis.router, prefix="/api/v1/ai-analysis", tags=["AI Analysis"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance", tags=["Maintenance Windows"])
app.include_router(metrics_dashboard.router, prefix="/api/v1/metrics", tags=["Metrics Dashboard"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(custom_reports.router, prefix="/api/v1/custom-reports", tags=["Custom Reports"])
app.include_router(backup.router, prefix="/api/v1/backup", tags=["Backup"])
app.include_router(sensor_groups.router, prefix="/api/v1/sensor-groups", tags=["Sensor Groups"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(probe_commands.router, prefix="/api/v1/probe-commands", tags=["Probe Commands"])
app.include_router(admin_tools.router, prefix="/api/v1/admin", tags=["Admin Tools"])
app.include_router(aiops.router, prefix="/api/v1/aiops", tags=["AIOps"])
app.include_router(noc.router, prefix="/api/v1/noc", tags=["NOC"])
app.include_router(noc_realtime.router, prefix="/api/v1/noc-realtime", tags=["NOC Real-Time"])
app.include_router(test_tools.router, prefix="/api/v1/test-tools", tags=["Test Tools"])
app.include_router(knowledge_base.router, prefix="/api/v1/knowledge-base", tags=["Knowledge Base"])
app.include_router(seed_kb.router, prefix="/api/v1/seed-kb", tags=["Seed Knowledge Base"])
app.include_router(ai_activities.router, prefix="/api/v1/ai-activities", tags=["AI Activities"])
app.include_router(ai_config.router, prefix="/api/v1/ai", tags=["AI Configuration"])
app.include_router(threshold_config.router, prefix="/api/v1/thresholds", tags=["Threshold Configuration"])
app.include_router(credentials.router)  # Credenciais (já tem prefix no router)
app.include_router(kubernetes.router)  # Já tem prefix no router
app.include_router(kubernetes_alerts.router)  # Alertas Kubernetes
app.include_router(security_monitor.router, prefix="/api/v1", tags=["Security Monitor"])
app.include_router(system_reset.router)  # System Reset
app.include_router(timescale_migration.router)  # TimescaleDB Migration
app.include_router(multi_probe.router)  # Multi-Probe Management
app.include_router(probe_nodes.router)  # Probe Nodes distribuídos
app.include_router(metrics_batch.router)  # Ingestão em lote de métricas
app.include_router(ws_dashboard.router, prefix="/api/v1")   # WebSocket Dashboard tempo real
app.include_router(discovery.router)      # Discovery de rede/SNMP/WMI
app.include_router(observability.router)  # Observability v3 (health-score, impact-map, intelligent alerts, WS)
app.include_router(topology.router)       # Topology v3 (graph, impact, nodes)
app.include_router(aiops_v3.router)       # AIOps v3 pipeline activities + feedback metrics
app.include_router(aiops_pipeline.router) # AIOps Pipeline v3 (run, simulate, logs, runs)
app.include_router(internal_health.router) # Meta observability — deep health check
app.include_router(sensor_controls.router, prefix="/api/v1/sensors", tags=["Sensor Controls"])
app.include_router(service_map.router)        # Service Map v3.5
app.include_router(audit.router)              # Audit Log v3.5
app.include_router(predictions.router)        # Failure Predictions v3.5
app.include_router(service_monitor.router, prefix="/api/v1", tags=["Service Monitor"])  # Service discovery sync
app.include_router(default_sensor_profiles.router, prefix="/api/v1", tags=["Default Sensor Profiles"])
app.include_router(hyperv.router)              # Hyper-V Observability REST API
app.include_router(hyperv_ws.router)           # Hyper-V WebSocket real-time

@app.get("/")
async def root():
    return {"message": "Coruja Monitor API", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
