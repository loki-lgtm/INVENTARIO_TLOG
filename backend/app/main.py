from fastapi import FastAPI

from app.routers import checklist

app = FastAPI(title="Sistema de Gestão de TI — Tlog")

app.include_router(checklist.router, prefix="/api")
