from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import checklist, estoque

app = FastAPI(title="Sistema de Gestão de TI — Tlog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(checklist.router, prefix="/api")
app.include_router(estoque.router, prefix="/api")
