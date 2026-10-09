"""Regras de negócio do checklist de periféricos por colaborador.

Princípio central: a matriz é sempre completa. Todo colaborador ativo aparece
com todos os periféricos ativos, e um item sem linha no banco vale `False`.
A ausência de registro nunca vira "desconhecido" — era exatamente o defeito do
`data.json` antigo, em que nem todo registro tinha as chaves preenchidas.
"""

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.centro_custo import CentroCusto
from app.models.checklist import ChecklistItem
from app.models.colaborador import Colaborador
from app.models.tipo_periferico import TipoPeriferico
from app.schemas.checklist import (
    CentroCustoOut,
    CentroCustoResumo,
    ChecklistPage,
    ColaboradorChecklistOut,
    ItemChecklistOut,
    MarcacaoIn,
    MarcacaoOut,
    TipoPerifericoOut,
)


def listar_tipos(db: Session) -> list[TipoPeriferico]:
    stmt = (
        select(TipoPeriferico)
        .where(TipoPeriferico.ativo.is_(True))
        .order_by(TipoPeriferico.ordem, TipoPeriferico.nome)
    )
    return list(db.scalars(stmt).all())


def _matriz_do_colaborador(
    colaborador: Colaborador,
    tipos: list[TipoPeriferico],
    marcacoes: dict[tuple[int, int], ChecklistItem],
) -> ColaboradorChecklistOut:
    itens: list[ItemChecklistOut] = []
    entregues = 0

    for tipo in tipos:
        registro = marcacoes.get((colaborador.id, tipo.id))
        entregue = bool(registro and registro.entregue)
        if entregue:
            entregues += 1
        itens.append(
            ItemChecklistOut(
                tipo_periferico_id=tipo.id,
                entregue=entregue,
                data_entrega=registro.data_entrega if registro else None,
                marcado_por=registro.marcado_por if registro else None,
            )
        )

    total = len(tipos)
    return ColaboradorChecklistOut(
        id=colaborador.id,
        nome=colaborador.nome,
        email=colaborador.email,
        cargo=colaborador.cargo,
        centro_custo=(
            CentroCustoOut.model_validate(colaborador.centro_custo)
            if colaborador.centro_custo
            else None
        ),
        itens=itens,
        entregues=entregues,
        total=total,
        completo=total > 0 and entregues == total,
    )


def listar_checklist(
    db: Session,
    centro_custo_id: int | None = None,
    busca: str | None = None,
    apenas_pendentes: bool = False,
    pagina: int = 1,
    tamanho_pagina: int = 50,
) -> ChecklistPage:
    tipos = listar_tipos(db)

    filtros = [Colaborador.ativo.is_(True)]
    if centro_custo_id is not None:
        filtros.append(Colaborador.centro_custo_id == centro_custo_id)
    if busca:
        alvo = f"%{busca.strip()}%"
        filtros.append(
            or_(Colaborador.nome.ilike(alvo), Colaborador.email.ilike(alvo))
        )

    total = db.scalar(select(func.count()).select_from(Colaborador).where(*filtros)) or 0

    stmt = (
        select(Colaborador)
        .where(*filtros)
        .options(selectinload(Colaborador.centro_custo))
        .order_by(Colaborador.nome)
        .offset((pagina - 1) * tamanho_pagina)
        .limit(tamanho_pagina)
    )
    colaboradores = list(db.scalars(stmt).all())

    # Uma única consulta para as marcações de toda a página.
    marcacoes: dict[tuple[int, int], ChecklistItem] = {}
    if colaboradores:
        ids = [c.id for c in colaboradores]
        registros = db.scalars(
            select(ChecklistItem).where(ChecklistItem.colaborador_id.in_(ids))
        ).all()
        marcacoes = {(r.colaborador_id, r.tipo_periferico_id): r for r in registros}

    linhas = [_matriz_do_colaborador(c, tipos, marcacoes) for c in colaboradores]

    if apenas_pendentes:
        linhas = [linha for linha in linhas if not linha.completo]

    return ChecklistPage(
        tipos=[TipoPerifericoOut.model_validate(t) for t in tipos],
        colaboradores=linhas,
        total=total,
        pagina=pagina,
        tamanho_pagina=tamanho_pagina,
    )


def marcar_item(
    db: Session,
    colaborador_id: int,
    tipo_periferico_id: int,
    dados: MarcacaoIn,
) -> MarcacaoOut:
    """Cria ou atualiza a marcação de um periférico. É o autosave da tela."""
    colaborador = db.get(Colaborador, colaborador_id)
    if colaborador is None:
        raise ValueError("Colaborador não encontrado.")

    tipo = db.get(TipoPeriferico, tipo_periferico_id)
    if tipo is None:
        raise ValueError("Tipo de periférico não encontrado.")
    if not tipo.ativo:
        raise ValueError(f"O periférico '{tipo.nome}' está inativo e não aceita marcação.")

    registro = db.scalar(
        select(ChecklistItem).where(
            ChecklistItem.colaborador_id == colaborador_id,
            ChecklistItem.tipo_periferico_id == tipo_periferico_id,
        )
    )

    if registro is None:
        registro = ChecklistItem(
            colaborador_id=colaborador_id, tipo_periferico_id=tipo_periferico_id
        )
        db.add(registro)

    registro.entregue = dados.entregue
    registro.marcado_por = dados.marcado_por
    registro.observacao = dados.observacao
    # Desmarcar limpa a data: uma entrega desfeita não tem data de entrega.
    registro.data_entrega = datetime.now(timezone.utc) if dados.entregue else None

    db.commit()
    db.refresh(registro)

    tipos = listar_tipos(db)
    entregues = (
        db.scalar(
            select(func.count())
            .select_from(ChecklistItem)
            .join(TipoPeriferico)
            .where(
                ChecklistItem.colaborador_id == colaborador_id,
                ChecklistItem.entregue.is_(True),
                TipoPeriferico.ativo.is_(True),
            )
        )
        or 0
    )
    total = len(tipos)

    return MarcacaoOut(
        colaborador_id=colaborador_id,
        tipo_periferico_id=tipo_periferico_id,
        entregue=registro.entregue,
        data_entrega=registro.data_entrega,
        marcado_por=registro.marcado_por,
        entregues=entregues,
        total=total,
        completo=total > 0 and entregues == total,
    )


def resumo_por_setor(db: Session) -> list[CentroCustoResumo]:
    """Base do relatório por setor pedido no MAPA.md."""
    total_tipos = len(listar_tipos(db))

    contagem_colaboradores = dict(
        db.execute(
            select(Colaborador.centro_custo_id, func.count(Colaborador.id))
            .where(Colaborador.ativo.is_(True))
            .group_by(Colaborador.centro_custo_id)
        ).all()
    )

    contagem_entregues = dict(
        db.execute(
            select(Colaborador.centro_custo_id, func.count(ChecklistItem.id))
            .join(ChecklistItem, ChecklistItem.colaborador_id == Colaborador.id)
            .join(TipoPeriferico, TipoPeriferico.id == ChecklistItem.tipo_periferico_id)
            .where(
                Colaborador.ativo.is_(True),
                ChecklistItem.entregue.is_(True),
                TipoPeriferico.ativo.is_(True),
            )
            .group_by(Colaborador.centro_custo_id)
        ).all()
    )

    # Colaboradores com todos os periféricos ativos entregues.
    sub = (
        select(
            Colaborador.centro_custo_id.label("cc"),
            Colaborador.id.label("colab"),
            func.count(ChecklistItem.id).label("qtd"),
        )
        .join(ChecklistItem, ChecklistItem.colaborador_id == Colaborador.id)
        .join(TipoPeriferico, TipoPeriferico.id == ChecklistItem.tipo_periferico_id)
        .where(
            Colaborador.ativo.is_(True),
            ChecklistItem.entregue.is_(True),
            TipoPeriferico.ativo.is_(True),
        )
        .group_by(Colaborador.centro_custo_id, Colaborador.id)
        .having(func.count(ChecklistItem.id) >= total_tipos)
        .subquery()
    )
    contagem_completos = dict(
        db.execute(select(sub.c.cc, func.count(sub.c.colab)).group_by(sub.c.cc)).all()
    )

    setores = db.scalars(
        select(CentroCusto).where(CentroCusto.ativo.is_(True)).order_by(CentroCusto.nome)
    ).all()

    resumo: list[CentroCustoResumo] = []
    for setor in setores:
        n_colab = contagem_colaboradores.get(setor.id, 0)
        previstos = n_colab * total_tipos
        entregues = contagem_entregues.get(setor.id, 0)
        resumo.append(
            CentroCustoResumo(
                id=setor.id,
                nome=setor.nome,
                total_colaboradores=n_colab,
                colaboradores_completos=contagem_completos.get(setor.id, 0),
                itens_entregues=entregues,
                itens_previstos=previstos,
                percentual=round(entregues / previstos * 100, 1) if previstos else 0.0,
            )
        )
    return resumo
