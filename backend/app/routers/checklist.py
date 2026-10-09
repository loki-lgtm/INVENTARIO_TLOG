from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.checklist import (
    CentroCustoResumo,
    ChecklistPage,
    MarcacaoIn,
    MarcacaoOut,
    TipoPerifericoOut,
)
from app.services import checklist_service

router = APIRouter(prefix="/checklist", tags=["Checklist"])


@router.get("/tipos", response_model=list[TipoPerifericoOut])
def listar_tipos(db: Session = Depends(get_db)):
    """Periféricos ativos, na ordem em que aparecem no termo."""
    return checklist_service.listar_tipos(db)


@router.get("/setores", response_model=list[CentroCustoResumo])
def resumo_setores(db: Session = Depends(get_db)):
    """Progresso de entrega por setor."""
    return checklist_service.resumo_por_setor(db)


@router.get("", response_model=ChecklistPage)
def listar_checklist(
    centro_custo_id: int | None = Query(default=None),
    busca: str | None = Query(default=None, max_length=180),
    apenas_pendentes: bool = Query(default=False),
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Matriz colaborador x periférico, sempre completa."""
    return checklist_service.listar_checklist(
        db,
        centro_custo_id=centro_custo_id,
        busca=busca,
        apenas_pendentes=apenas_pendentes,
        pagina=pagina,
        tamanho_pagina=tamanho_pagina,
    )


@router.put(
    "/{colaborador_id}/{tipo_periferico_id}",
    response_model=MarcacaoOut,
    status_code=status.HTTP_200_OK,
)
def marcar_item(
    colaborador_id: int,
    tipo_periferico_id: int,
    dados: MarcacaoIn,
    db: Session = Depends(get_db),
):
    """Marca ou desmarca a entrega de um periférico. Idempotente."""
    try:
        return checklist_service.marcar_item(
            db, colaborador_id, tipo_periferico_id, dados
        )
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
