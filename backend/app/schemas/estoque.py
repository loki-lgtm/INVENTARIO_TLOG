from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ItemEstoqueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    categoria: Optional[str] = None
    alerta_minimo: int
    ativo: bool


class SaldoEstadoOut(BaseModel):
    estado: Literal["novo", "usado", "defeituoso"]
    quantidade: int


class ItemSetorOut(BaseModel):
    item_estoque_id: int
    nome: str
    categoria: Optional[str] = None
    alerta_minimo: int
    saldos: list[SaldoEstadoOut]
    total: int
    abaixo_do_minimo: bool


class CentroCustoResumoEstoque(BaseModel):
    id: int
    nome: str
    total_itens: int
    total_defeituosos: int


class EstoqueSetorPage(BaseModel):
    centro_custo_id: int
    centro_custo_nome: str
    itens: list[ItemSetorOut]


class AtualizarSaldoIn(BaseModel):
    quantidade: int = Field(ge=0)
    observacao: Optional[str] = None
