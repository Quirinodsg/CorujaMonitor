from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from database import engine, Base
from routers import auth, tenants, probes, servers, sensors, metrics, incidents, reports, dashboard, probe_commands, users, sensor_notes, ai_analysis, notifications, maintenance, admin_tools, aiops, noc, noc_realtime, test_tools, knowledge_base, ai_activities, ai_config, threshold_config, seed_kb, custom_reports, backup, sensor_groups, kubernetes, kubernetes_alerts, metrics_dashboard, auth_config, security_monitor

# Importar WAF Middleware
try:
    from middleware.waf import WAFMiddleware
    WAF_AVAILABLE = True
except ImportError:
    WAF_AVAILABLE = False
    print("⚠️  WAF Middleware not available")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown

app = FastAPI(
    title="Coruja Monitor API",
    description="Enterprise monitoring platform with AIOps capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# WAF Middleware - DEVE ser adicionado ANTES do CORS
if WAF_AVAILABLE:
    app.add_middleware(WAFMiddleware)
    print("✅ WAF Middleware enabled")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
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
app.include_router(kubernetes.router)  # Já tem prefix no router
app.include_router(kubernetes_alerts.router)  # Alertas Kubernetes
app.include_router(security_monitor.router, prefix="/api/v1", tags=["Security Monitor"])

@app.get("/")
async def root():
    return {"message": "Coruja Monitor API", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
