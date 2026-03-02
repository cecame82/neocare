"""
Módulo principal de la API de NeoCare Health.
Configura la aplicación FastAPI, CORS y las rutas de los controladores.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import engine, SessionLocal
from app import models
from app.config import settings
from app.logger import get_logger
from app.routers import (
    auth,
    users,
    cards,
    lists,
    boards,
    worklogs,
    labels,
    labelTemplates,
    checklist,
)
from app.routers import report
from app.services.label_template_seed import seed_label_templates

# Obtener logger centralizado
logger = get_logger(__name__)

# Crear tablas en la base de datos si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)


@app.on_event("startup")
def startup_seed():
    """Semilla de datos al iniciar la aplicación."""
    logger.info("🚀 Startup ejecutándose - Ambiente: %s", settings.ENVIRONMENT)
    db = SessionLocal()
    try:
        seed_label_templates(db)
        logger.info("✅ Plantillas de etiquetas cargadas")
    except Exception as error:  # pylint: disable=broad-except
        logger.error("❌ Error en seeding: %s", str(error))
    finally:
        db.close()


# ============================================================
# 🚧 CORS UNIVERSAL — evita fallos de preflight en Railway/Render
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Puedes poner tu dominio exacto si quieres restringir
    allow_credentials=True,
    allow_methods=["*"],          # IMPORTANTE: permite OPTIONS
    allow_headers=["*"],          # IMPORTANTE: permite Content-Type
)

logger.info("✅ CORS universal configurado correctamente")


# ============================================================
# 🛡️ Middleware de Security Headers
# ============================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware que agrega headers de seguridad a todas las respuestas."""
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        for header, value in settings.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

app.add_middleware(SecurityHeadersMiddleware)
logger.info("✅ Security headers configurados")


# ============================================================
# 📌 Inclusión de Routers (Rutas de la API)
# ============================================================
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cards.router)
app.include_router(lists.router)
app.include_router(boards.router)
app.include_router(worklogs.router)
app.include_router(report.router)
app.include_router(labels.router)
app.include_router(labelTemplates.router)
app.include_router(checklist.router)


# ============================================================
# 🧩 Handler universal para OPTIONS — soluciona preflight
# ============================================================
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return {}


@app.get("/")
def read_root():
    """Ruta de bienvenida para verificar el estado de la API."""
    return {"message": "Bienvenidos a la API de NeoCare Health."}

