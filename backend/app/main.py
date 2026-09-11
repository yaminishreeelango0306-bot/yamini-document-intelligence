import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api.routes.documents import router as documents_router
from .core.database import init_db
from .core.logging import configure_logging
from .core.config import CORS_ORIGINS


configure_logging()

logger = logging.getLogger(__name__)

init_db()

app = FastAPI(
    title="Document Intelligence API",
    version="1.0.0",
    description="Financial document extraction, validation and persistence API."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(documents_router)

ROOT = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(
    directory=str(ROOT / "frontend" / "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=str(ROOT / "frontend" / "static")),
    name="static"
)


@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "service": "document-intelligence"
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request
        }
    )


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    logger.exception("Unhandled exception")

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred."
            }
        }
    )

