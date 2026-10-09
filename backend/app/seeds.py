"""Carga inicial do banco.

Os periféricos vêm do TERMO DE RESPONSABILIDADE da Tlog — os sete itens da
tabela "Periféricos", na ordem impressa no documento.

Os centros de custo vêm do MAPA.md. A lista ainda precisa de confirmação:
"CCO Fiscal" aparece em arquitetura-projeto.md e não está no MAPA.md, e não
foi esclarecido se é um setor próprio ou outro nome para Controladoria.
Está marcado abaixo e não foi incluído até a definição.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.centro_custo import CentroCusto
from app.models.tipo_periferico import TipoPeriferico

PERIFERICOS = [
    ("Mouse", "mouse"),
    ("Mousepad", "mousepad"),
    ("Teclado", "teclado"),
    ("Apoio de pulso", "apoio-de-pulso"),
    ("Suporte de notebook", "suporte-de-notebook"),
    ("Fone de ouvido", "fone-de-ouvido"),
    ("Hub USB", "hub-usb"),
]

CENTROS_CUSTO = [
    "Administrativo",
    "Comercial",
    "Contratos",
    "Controladoria",
    "Financeiro",
    "Manutenção",
    "TI",
    # PENDENTE: "CCO Fiscal" — confirmar se é setor próprio ou apelido de Controladoria.
]


def rodar_seed(db: Session) -> dict[str, int]:
    criados = {"perifericos": 0, "centros_custo": 0}

    for ordem, (nome, slug) in enumerate(PERIFERICOS, start=1):
        existe = db.scalar(select(TipoPeriferico).where(TipoPeriferico.slug == slug))
        if existe is None:
            db.add(TipoPeriferico(nome=nome, slug=slug, ordem=ordem, ativo=True))
            criados["perifericos"] += 1

    for nome in CENTROS_CUSTO:
        existe = db.scalar(select(CentroCusto).where(CentroCusto.nome == nome))
        if existe is None:
            db.add(CentroCusto(nome=nome, ativo=True))
            criados["centros_custo"] += 1

    db.commit()
    return criados


if __name__ == "__main__":
    from app.db.database import SessionLocal, engine
    from app.models import Base

    Base.metadata.create_all(engine)
    with SessionLocal() as sessao:
        print(rodar_seed(sessao))
