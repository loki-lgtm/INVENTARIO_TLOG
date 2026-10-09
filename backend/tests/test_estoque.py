"""Testes do módulo de estoque por setor.

Rodam em SQLite na memória para não exigir Postgres no CI.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.db.database import get_db
from app.main import app
from app.models import Base
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

    def _get_db():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_seed_cria_os_dez_itens_do_catalogo(cliente):
    resposta = cliente.get("/api/estoque/itens")
    assert resposta.status_code == 200
    nomes = [i["nome"] for i in resposta.json()]
    assert nomes == [
        "Cabo HDMI 1.8m",
        "Estabilizador 300VA",
        "Headset USB",
        "Monitor 24 polegadas",
        "Mouse USB",
        "Mousepad",
        "Notebook Dell 14 polegadas",
        "Suporte para notebook",
        "Teclado ABNT2",
        "Webcam Full HD",
    ]


def test_resumo_por_setor_traz_todos_os_setores_ativos_com_zeros(cliente):
    resposta = cliente.get("/api/estoque/setores")
    assert resposta.status_code == 200
    setores = resposta.json()
    assert len(setores) == 7
    for setor in setores:
        assert setor["total_itens"] == 0
        assert setor["total_defeituosos"] == 0


def test_matriz_do_setor_vem_completa_mesmo_sem_lancamento(cliente):
    setores = cliente.get("/api/estoque/setores").json()
    setor_id = setores[0]["id"]

    dados = cliente.get(f"/api/estoque/{setor_id}").json()
    assert dados["centro_custo_id"] == setor_id
    assert len(dados["itens"]) == 10
    for item in dados["itens"]:
        assert len(item["saldos"]) == 3
        estados = {s["estado"] for s in item["saldos"]}
        assert estados == {"novo", "usado", "defeituoso"}
        assert all(s["quantidade"] == 0 for s in item["saldos"])
        assert item["total"] == 0


def test_atualizar_saldo_reflete_no_setor_e_no_resumo(cliente):
    setores = cliente.get("/api/estoque/setores").json()
    setor_id = setores[0]["id"]
    item_id = cliente.get("/api/estoque/itens").json()[0]["id"]

    resposta = cliente.put(
        f"/api/estoque/{setor_id}/{item_id}/novo",
        json={"quantidade": 5, "observacao": "Compra inicial"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["estado"] == "novo"
    assert corpo["quantidade"] == 5

    dados_setor = cliente.get(f"/api/estoque/{setor_id}").json()
    linha = next(i for i in dados_setor["itens"] if i["item_estoque_id"] == item_id)
    assert linha["total"] == 5
    saldo_novo = next(s for s in linha["saldos"] if s["estado"] == "novo")
    assert saldo_novo["quantidade"] == 5

    resumo = cliente.get("/api/estoque/setores").json()
    resumido = next(s for s in resumo if s["id"] == setor_id)
    assert resumido["total_itens"] == 5
    assert resumido["total_defeituosos"] == 0


def test_estados_diferentes_do_mesmo_item_nao_se_sobrescrevem(cliente):
    setores = cliente.get("/api/estoque/setores").json()
    setor_id = setores[0]["id"]
    item_id = cliente.get("/api/estoque/itens").json()[0]["id"]

    cliente.put(f"/api/estoque/{setor_id}/{item_id}/novo", json={"quantidade": 5})
    cliente.put(f"/api/estoque/{setor_id}/{item_id}/defeituoso", json={"quantidade": 2})

    dados_setor = cliente.get(f"/api/estoque/{setor_id}").json()
    linha = next(i for i in dados_setor["itens"] if i["item_estoque_id"] == item_id)
    saldos = {s["estado"]: s["quantidade"] for s in linha["saldos"]}
    assert saldos["novo"] == 5
    assert saldos["defeituoso"] == 2
    assert saldos["usado"] == 0
    assert linha["total"] == 7

    resumo = cliente.get("/api/estoque/setores").json()
    resumido = next(s for s in resumo if s["id"] == setor_id)
    assert resumido["total_itens"] == 7
    assert resumido["total_defeituosos"] == 2


def test_estado_invalido_retorna_422(cliente):
    setores = cliente.get("/api/estoque/setores").json()
    setor_id = setores[0]["id"]
    item_id = cliente.get("/api/estoque/itens").json()[0]["id"]

    resposta = cliente.put(
        f"/api/estoque/{setor_id}/{item_id}/quebrado", json={"quantidade": 1}
    )
    assert resposta.status_code == 422


def test_setor_inexistente_retorna_404(cliente):
    resposta = cliente.get("/api/estoque/9999")
    assert resposta.status_code == 404
