import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { estoqueService } from "../../services/estoqueService";
import "./EstoquePorSetor.css";

const ESTADOS = [
  { chave: "novo", rotulo: "Novo" },
  { chave: "usado", rotulo: "Usado" },
  { chave: "defeituoso", rotulo: "Defeituoso" },
];

function obterQuantidade(item, estado) {
  return item.saldos.find((s) => s.estado === estado)?.quantidade ?? 0;
}

function calcularTotal(item) {
  return item.saldos.reduce((soma, s) => soma + s.quantidade, 0);
}

function rotuloEstado(estado) {
  return ESTADOS.find((e) => e.chave === estado)?.rotulo ?? estado;
}

export default function EstoquePorSetor() {
  const [setores, setSetores] = useState([]);
  const [setorAtivo, setSetorAtivo] = useState(null);
  const [dadosSetor, setDadosSetor] = useState(null);

  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  const [salvando, setSalvando] = useState(() => new Set());

  const requisicaoAtual = useRef(0);
  // Guarda o valor com que uma célula entrou em edição, pra poder desfazer
  // se o PUT falhar. Fica vazio entre focos — não é estado de render.
  const valorOriginalRef = useRef({});

  const carregarSetores = useCallback(async () => {
    try {
      setSetores(await estoqueService.listarSetores());
    } catch (e) {
      setErro(e.message);
    }
  }, []);

  const carregarDados = useCallback(async () => {
    if (setorAtivo == null) return;
    const marca = ++requisicaoAtual.current;
    setCarregando(true);
    try {
      const dados = await estoqueService.buscarPorSetor(setorAtivo);
      // Descarta respostas de trocas de setor já superadas.
      if (marca !== requisicaoAtual.current) return;
      setDadosSetor(dados);
      setErro(null);
    } catch (e) {
      if (marca === requisicaoAtual.current) setErro(e.message);
    } finally {
      if (marca === requisicaoAtual.current) setCarregando(false);
    }
  }, [setorAtivo]);

  useEffect(() => {
    carregarSetores();
  }, [carregarSetores]);

  // Sem setor escolhido ainda: assume o primeiro assim que a lista chega.
  useEffect(() => {
    if (setorAtivo === null && setores.length > 0) {
      setSetorAtivo(setores[0].id);
    }
  }, [setores, setorAtivo]);

  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

  function handleChange(itemEstoqueId, estado, valorTexto) {
    const numero = Number(valorTexto);
    const quantidade =
      valorTexto === "" || !Number.isFinite(numero) ? 0 : Math.max(0, Math.trunc(numero));

    // Atualização otimista: o campo responde na hora, sem esperar o servidor.
    setDadosSetor((atual) => {
      if (!atual) return atual;
      return {
        ...atual,
        itens: atual.itens.map((item) => {
          if (item.item_estoque_id !== itemEstoqueId) return item;
          return {
            ...item,
            saldos: item.saldos.map((s) =>
              s.estado === estado ? { ...s, quantidade } : s
            ),
          };
        }),
      };
    });
  }

  function handleFocus(item, estado) {
    const chave = `${item.item_estoque_id}:${estado}`;
    if (!(chave in valorOriginalRef.current)) {
      valorOriginalRef.current[chave] = obterQuantidade(item, estado);
    }
  }

  function reverterCelula(itemEstoqueId, estado, quantidade) {
    setDadosSetor((atual) => {
      if (!atual) return atual;
      return {
        ...atual,
        itens: atual.itens.map((item) => {
          if (item.item_estoque_id !== itemEstoqueId) return item;
          return {
            ...item,
            saldos: item.saldos.map((s) =>
              s.estado === estado ? { ...s, quantidade } : s
            ),
          };
        }),
      };
    });
  }

  async function handleBlur(item, estado) {
    const chave = `${item.item_estoque_id}:${estado}`;
    const original = valorOriginalRef.current[chave];
    delete valorOriginalRef.current[chave];

    const quantidadeNova = obterQuantidade(item, estado);
    // Sem edição real (só passou o foco pela célula): nada a salvar.
    if (original === undefined || original === quantidadeNova) return;

    setSalvando((s) => new Set(s).add(chave));

    try {
      await estoqueService.atualizarSaldo(setorAtivo, item.item_estoque_id, estado, {
        quantidade: quantidadeNova,
      });
      carregarSetores();
    } catch (e) {
      // Falhou: volta ao valor confirmado em vez de mentir na tela.
      reverterCelula(item.item_estoque_id, estado, original);
      setErro(
        `Não foi possível salvar "${rotuloEstado(estado)}" de ${item.nome}. ${e.message}`
      );
    } finally {
      setSalvando((s) => {
        const proximo = new Set(s);
        proximo.delete(chave);
        return proximo;
      });
    }
  }

  const geral = useMemo(() => {
    const totalItens = setores.reduce((soma, s) => soma + s.total_itens, 0);
    const totalDefeituosos = setores.reduce((soma, s) => soma + s.total_defeituosos, 0);
    return { totalItens, totalDefeituosos };
  }, [setores]);

  const itens = dadosSetor?.itens ?? [];

  return (
    <div className="est">
      <header className="est-topo">
        <div>
          <h1 className="est-titulo">Estoque por setor</h1>
          <p className="est-sub">
            {setores.length} setores · {geral.totalItens} itens no total
          </p>
        </div>
        <div className="est-medidor" aria-hidden="true">
          <div className="est-medidor-num">{geral.totalDefeituosos}</div>
          <div className="est-medidor-txt">itens defeituosos</div>
        </div>
      </header>

      {erro && (
        <div className="est-erro" role="alert">
          <span>{erro}</span>
          <button
            type="button"
            onClick={() => {
              carregarSetores();
              carregarDados();
            }}
          >
            Tentar de novo
          </button>
        </div>
      )}

      <div className="est-corpo">
        <nav className="est-setores" aria-label="Selecionar setor">
          {setores.map((setor) => (
            <button
              key={setor.id}
              type="button"
              className={`est-setor ${setorAtivo === setor.id ? "esta-ativo" : ""}`}
              onClick={() => setSetorAtivo(setor.id)}
            >
              <span className="est-setor-nome">{setor.nome}</span>
              <span className="est-setor-num">{setor.total_itens}</span>
              {setor.total_defeituosos > 0 && (
                <span className="est-setor-defeito">
                  {setor.total_defeituosos} defeituoso
                  {setor.total_defeituosos > 1 ? "s" : ""}
                </span>
              )}
            </button>
          ))}

          {!carregando && setores.length === 0 && (
            <p className="est-setores-vazio">Nenhum setor cadastrado.</p>
          )}
        </nav>

        <section className="est-painel">
          <div className="est-filtros">
            <span className="est-setor-atual">{dadosSetor?.centro_custo_nome ?? "—"}</span>
            <span className="est-contagem">{itens.length} itens</span>
          </div>

          <div className="est-rolagem">
            <table className="est-tabela">
              <thead>
                <tr>
                  <th scope="col" className="est-col-nome">
                    Item
                  </th>
                  {ESTADOS.map((estado) => (
                    <th
                      key={estado.chave}
                      scope="col"
                      className={`est-col-estado est-col-${estado.chave}`}
                    >
                      {estado.rotulo}
                    </th>
                  ))}
                  <th scope="col" className="est-col-total">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody>
                {itens.map((item) => {
                  const total = calcularTotal(item);
                  const abaixoDoMinimo = total < item.alerta_minimo;
                  return (
                    <tr
                      key={item.item_estoque_id}
                      className={abaixoDoMinimo ? "esta-abaixo" : ""}
                    >
                      <th scope="row" className="est-col-nome">
                        <span className="est-item-nome">{item.nome}</span>
                        <span className="est-item-categoria">{item.categoria || "—"}</span>
                      </th>

                      {ESTADOS.map((estado) => {
                        const chave = `${item.item_estoque_id}:${estado.chave}`;
                        return (
                          <td key={estado.chave} className={`est-col-estado est-col-${estado.chave}`}>
                            <input
                              type="number"
                              min="0"
                              step="1"
                              inputMode="numeric"
                              className="est-input"
                              value={obterQuantidade(item, estado.chave)}
                              disabled={salvando.has(chave)}
                              onChange={(e) =>
                                handleChange(item.item_estoque_id, estado.chave, e.target.value)
                              }
                              onFocus={() => handleFocus(item, estado.chave)}
                              onBlur={() => handleBlur(item, estado.chave)}
                              aria-label={`${estado.rotulo} de ${item.nome}`}
                            />
                          </td>
                        );
                      })}

                      <td className="est-col-total">
                        <span className="est-total">
                          {total}
                          {item.alerta_minimo > 0 && (
                            <span className="est-minimo"> / mín. {item.alerta_minimo}</span>
                          )}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {!carregando && itens.length === 0 && (
              <p className="est-vazio">
                {setorAtivo
                  ? "Nenhum item de estoque cadastrado neste setor."
                  : "Selecione um setor para ver o estoque."}
              </p>
            )}

            {carregando && <p className="est-vazio">Carregando…</p>}
          </div>
        </section>
      </div>
    </div>
  );
}
