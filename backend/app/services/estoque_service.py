"""Regras de negócio do estoque de equipamentos por setor.

Princípio central: a matriz é sempre completa, o mesmo princípio do
checklist. Todo item ativo aparece para todo setor, com os três estados de
conservação, e uma combinação sem linha em `estoque_setor` vale quantidade 0
— nunca "desconhecido".
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.centro_custo import CentroCusto
from app.models.estoque_setor import EstoqueSetor
from app.models.item_estoque import ItemEstoque
from app.schemas.estoque import (
    AtualizarSaldoIn,
    CentroCustoResumoEstoque,
    EstoqueSetorPage,
    ItemSetorOut,
    SaldoEstadoOut,
)

ESTADOS = ["novo", "usado", "defeituoso"]


def listar_itens(db: Session) -> list[ItemEstoque]:
    stmt = (
        select(ItemEstoque).where(ItemEstoque.ativo.is_(True)).order_by(ItemEstoque.nome)
    )
    return list(db.scalars(stmt).all())


def resumo_por_setor(db: Session) -> list[CentroCustoResumoEstoque]:
    total_por_setor = dict(
        db.execute(
            select(EstoqueSetor.centro_custo_id, func.sum(EstoqueSetor.quantidade)).group_by(
                EstoqueSetor.centro_custo_id
            )
        ).all()
    )
    defeituosos_por_setor = dict(
        db.execute(
            select(EstoqueSetor.centro_custo_id, func.sum(EstoqueSetor.quantidade))
            .where(EstoqueSetor.estado == "defeituoso")
            .group_by(EstoqueSetor.centro_custo_id)
        ).all()
    )

    setores = db.scalars(
        select(CentroCusto).where(CentroCusto.ativo.is_(True)).order_by(CentroCusto.nome)
    ).all()

    return [
        CentroCustoResumoEstoque(
            id=setor.id,
            nome=setor.nome,
            total_itens=total_por_setor.get(setor.id, 0),
            total_defeituosos=defeituosos_por_setor.get(setor.id, 0),
        )
        for setor in setores
    ]


def estoque_do_setor(db: Session, centro_custo_id: int) -> EstoqueSetorPage:
    setor = db.get(CentroCusto, centro_custo_id)
    if setor is None:
        raise ValueError("Centro de custo não encontrado.")

    itens = listar_itens(db)

    saldos: dict[tuple[int, str], int] = {}
    if itens:
        ids = [item.id for item in itens]
        registros = db.scalars(
            select(EstoqueSetor).where(
                EstoqueSetor.centro_custo_id == centro_custo_id,
                EstoqueSetor.item_estoque_id.in_(ids),
            )
        ).all()
        saldos = {(r.item_estoque_id, r.estado): r.quantidade for r in registros}

    linhas: list[ItemSetorOut] = []
    for item in itens:
        saldos_item = [
            SaldoEstadoOut(estado=estado, quantidade=saldos.get((item.id, estado), 0))
            for estado in ESTADOS
        ]
        total = sum(s.quantidade for s in saldos_item)
        linhas.append(
            ItemSetorOut(
                item_estoque_id=item.id,
                nome=item.nome,
                categoria=item.categoria,
                alerta_minimo=item.alerta_minimo,
                saldos=saldos_item,
                total=total,
                abaixo_do_minimo=total < item.alerta_minimo,
            )
        )

    return EstoqueSetorPage(
        centro_custo_id=setor.id, centro_custo_nome=setor.nome, itens=linhas
    )


def atualizar_saldo(
    db: Session,
    centro_custo_id: int,
    item_estoque_id: int,
    estado: str,
    dados: AtualizarSaldoIn,
) -> SaldoEstadoOut:
    """Cria ou atualiza o saldo de um item em um estado. É o autosave da tela."""
    setor = db.get(CentroCusto, centro_custo_id)
    if setor is None:
        raise ValueError("Centro de custo não encontrado.")

    item = db.get(ItemEstoque, item_estoque_id)
    if item is None:
        raise ValueError("Item de estoque não encontrado.")

    registro = db.scalar(
        select(EstoqueSetor).where(
            EstoqueSetor.centro_custo_id == centro_custo_id,
            EstoqueSetor.item_estoque_id == item_estoque_id,
            EstoqueSetor.estado == estado,
        )
    )

    if registro is None:
        registro = EstoqueSetor(
            centro_custo_id=centro_custo_id,
            item_estoque_id=item_estoque_id,
            estado=estado,
        )
        db.add(registro)

    registro.quantidade = dados.quantidade
    registro.observacao = dados.observacao

    db.commit()
    db.refresh(registro)

    return SaldoEstadoOut(estado=registro.estado, quantidade=registro.quantidade)
