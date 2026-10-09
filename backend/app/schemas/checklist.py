from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TipoPerifericoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    slug: str
    ordem: int
    ativo: bool
    observacao: Optional[str] = None


class CentroCustoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class CentroCustoResumo(BaseModel):
    id: int
    nome: str
    total_colaboradores: int
    colaboradores_completos: int
    itens_entregues: int
    itens_previstos: int
    percentual: float


class ItemChecklistOut(BaseModel):
    tipo_periferico_id: int
    entregue: bool
    data_entrega: Optional[datetime] = None
    marcado_por: Optional[str] = None


class ColaboradorChecklistOut(BaseModel):
    id: int
    nome: str
    email: str
    cargo: Optional[str] = None
    centro_custo: Optional[CentroCustoOut] = None
    itens: list[ItemChecklistOut]
    entregues: int
    total: int
    completo: bool


class ChecklistPage(BaseModel):
    tipos: list[TipoPerifericoOut]
    colaboradores: list[ColaboradorChecklistOut]
    total: int
    pagina: int
    tamanho_pagina: int


class MarcacaoIn(BaseModel):
    entregue: bool
    marcado_por: Optional[str] = None
    observacao: Optional[str] = None


class MarcacaoOut(BaseModel):
    colaborador_id: int
    tipo_periferico_id: int
    entregue: bool
    data_entrega: Optional[datetime] = None
    marcado_por: Optional[str] = None
    entregues: int
    total: int
    completo: bool
