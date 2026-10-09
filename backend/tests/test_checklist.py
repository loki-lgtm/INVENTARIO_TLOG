"""Testes do módulo de checklist.

Rodam em SQLite na memória para não exigir Postgres no CI.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.db.database import get_db
from app.main import app
from app.models import Base, CentroCusto, Colaborador
from app.seeds import rodar_seed


@pytest.fixture()
def cliente():
    # StaticPool: sem ele, cada conexao ao SQLite em memoria abre um banco
    # vazio e as tabelas criadas aqui somem para o TestClient.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Sessao = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    with Sessao() as sessao:
        rodar_seed(sessao)
        centro = sessao.query(CentroCusto).first()
        sessao.add_all(
            [
                Colaborador(
                    nome="Ana Ribeiro",
                    email="ana.ribeiro@tlog.com.br",
                    cargo="Analista",
                    centro_custo_id=centro.id,
                ),
                Colaborador(
                    nome="Bruno Sales",
                    email="bruno.sales@tlog.com.br",
                    cargo="Assistente",
                    centro_custo_id=centro.id,
                ),
            ]
        )
        sessao.commit()

    def _get_db():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_seed_cria_os_sete_perifericos_do_termo(cliente):
    resposta = cliente.get("/api/checklist/tipos")
    assert resposta.status_code == 200
    nomes = [t["nome"] for t in resposta.json()]
    assert nomes == [
        "Mouse",
        "Mousepad",
        "Teclado",
        "Apoio de pulso",
        "Suporte de notebook",
        "Fone de ouvido",
        "Hub USB",
    ]


def test_matriz_vem_completa_mesmo_sem_marcacao(cliente):
    """O defeito do data.json antigo: registro sem todas as chaves."""
    dados = cliente.get("/api/checklist").json()
    assert dados["total"] == 2
    for linha in dados["colaboradores"]:
        assert len(linha["itens"]) == 7
        assert all(item["entregue"] is False for item in linha["itens"])
        assert linha["entregues"] == 0
        assert linha["completo"] is False


def test_marcar_e_desmarcar_item(cliente):
    dados = cliente.get("/api/checklist").json()
    colaborador = dados["colaboradores"][0]
    tipo = dados["tipos"][0]

    marcado = cliente.put(
        f"/api/checklist/{colaborador['id']}/{tipo['id']}",
        json={"entregue": True, "marcado_por": "suporte.ti@tlog.com.br"},
    ).json()
    assert marcado["entregue"] is True
    assert marcado["data_entrega"] is not None
    assert marcado["entregues"] == 1

    desmarcado = cliente.put(
        f"/api/checklist/{colaborador['id']}/{tipo['id']}",
        json={"entregue": False},
    ).json()
    assert desmarcado["entregue"] is False
    assert desmarcado["data_entrega"] is None
    assert desmarcado["entregues"] == 0


def test_colaborador_fica_completo_com_os_sete(cliente):
    dados = cliente.get("/api/checklist").json()
    colaborador = dados["colaboradores"][0]

    for tipo in dados["tipos"]:
        resposta = cliente.put(
            f"/api/checklist/{colaborador['id']}/{tipo['id']}",
            json={"entregue": True, "marcado_por": "suporte.ti@tlog.com.br"},
        )
        assert resposta.status_code == 200

    assert resposta.json()["completo"] is True


def test_busca_por_nome_e_email(cliente):
    assert cliente.get("/api/checklist?busca=Ana").json()["total"] == 1
    assert cliente.get("/api/checklist?busca=bruno.sales").json()["total"] == 1
    assert cliente.get("/api/checklist?busca=inexistente").json()["total"] == 0


def test_resumo_por_setor(cliente):
    dados = cliente.get("/api/checklist").json()
    colaborador = dados["colaboradores"][0]
    for tipo in dados["tipos"][:3]:
        cliente.put(
            f"/api/checklist/{colaborador['id']}/{tipo['id']}", json={"entregue": True}
        )

    setores = cliente.get("/api/checklist/setores").json()
    ativo = next(s for s in setores if s["total_colaboradores"] > 0)
    assert ativo["total_colaboradores"] == 2
    assert ativo["itens_previstos"] == 14
    assert ativo["itens_entregues"] == 3
    assert ativo["colaboradores_completos"] == 0


def test_tipo_inexistente_retorna_404(cliente):
    dados = cliente.get("/api/checklist").json()
    colaborador = dados["colaboradores"][0]
    resposta = cliente.put(
        f"/api/checklist/{colaborador['id']}/9999", json={"entregue": True}
    )
    assert resposta.status_code == 404
