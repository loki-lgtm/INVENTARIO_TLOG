from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.estoque import (
    AtualizarSaldoIn,
    CentroCustoResumoEstoque,
    EstoqueSetorPage,
    ItemEstoqueOut,
    SaldoEstadoOut,
)
from app.services import estoque_service

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("/itens", response_model=list[ItemEstoqueOut])
def listar_itens(db: Session = Depends(get_db)):
    """Catálogo de tipos de equipamento ativos, em ordem alfabética."""
    return estoque_service.listar_itens(db)


@router.get("/setores", response_model=list[CentroCustoResumoEstoque])
def resumo_setores(db: Session = Depends(get_db)):
    """Total em estoque e total defeituoso por setor."""
    return estoque_service.resumo_por_setor(db)


@router.get("/{centro_custo_id}", response_model=EstoqueSetorPage)
def estoque_do_setor(centro_custo_id: int, db: Session = Depends(get_db)):
    """Matriz item x estado de conservação de um setor, sempre completa."""
    try:
        return estoque_service.estoque_do_setor(db, centro_custo_id)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))


@router.put(
    "/{centro_custo_id}/{item_estoque_id}/{estado}",
    response_model=SaldoEstadoOut,
    status_code=status.HTTP_200_OK,
)
def atualizar_saldo(
    centro_custo_id: int,
    item_estoque_id: int,
    estado: Literal["novo", "usado", "defeituoso"],
    dados: AtualizarSaldoIn,
    db: Session = Depends(get_db),
):
    """Atualiza a quantidade de um item, em um estado, em um setor. Idempotente."""
    try:
        return estoque_service.atualizar_saldo(
            db, centro_custo_id, item_estoque_id, estado, dados
        )
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
