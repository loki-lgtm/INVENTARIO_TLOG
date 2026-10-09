import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { checklistService } from "../../services/checklistService";
import "./Checklist.css";

// Enquanto a autenticação não existe, a marcação é atribuída a este operador.
// Trocar por AuthContext quando o módulo de login entrar.
const OPERADOR_ATUAL = "suporte.ti@tlog.com.br";

function abreviar(nome) {
  const palavras = nome.split(" ").filter(Boolean);
  if (palavras.length === 1) return palavras[0].slice(0, 3);
  return palavras
    .slice(0, 2)
    .map((p) => p[0])
    .join("");
}

export default function Checklist() {
  const [setores, setSetores] = useState([]);
  const [setorAtivo, setSetorAtivo] = useState(null);
  const [busca, setBusca] = useState("");
  const [buscaAplicada, setBuscaAplicada] = useState("");
  const [apenasPendentes, setApenasPendentes] = useState(false);

  const [tipos, setTipos] = useState([]);
  const [linhas, setLinhas] = useState([]);
  const [total, setTotal] = useState(0);

  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  const [salvando, setSalvando] = useState(() => new Set());

  const requisicaoAtual = useRef(0);

  useEffect(() => {
    const id = setTimeout(() => setBuscaAplicada(busca), 300);
    return () => clearTimeout(id);
  }, [busca]);

  const carregarSetores = useCallback(async () => {
    try {
      setSetores(await checklistService.listarSetores());
    } catch (e) {
      setErro(e.message);
    }
  }, []);

  const carregarLinhas = useCallback(async () => {
    const marca = ++requisicaoAtual.current;
    setCarregando(true);
    try {
      const dados = await checklistService.listar({
        centroCustoId: setorAtivo,
        busca: buscaAplicada,
        apenasPendentes,
      });
      // Descarta respostas de buscas já superadas.
      if (marca !== requisicaoAtual.current) return;
      setTipos(dados.tipos);
      setLinhas(dados.colaboradores);
      setTotal(dados.total);
      setErro(null);
    } catch (e) {
      if (marca === requisicaoAtual.current) setErro(e.message);
    } finally {
      if (marca === requisicaoAtual.current) setCarregando(false);
    }
  }, [setorAtivo, buscaAplicada, apenasPendentes]);

  useEffect(() => {
    carregarSetores();
  }, [carregarSetores]);

  useEffect(() => {
    carregarLinhas();
  }, [carregarLinhas]);

  async function alternar(colaborador, tipo, entregue) {
    const chave = `${colaborador.id}:${tipo.id}`;
    const anterior = linhas;

    // Atualização otimista: a marcação responde na hora.
    setLinhas((atuais) =>
      atuais.map((linha) => {
        if (linha.id !== colaborador.id) return linha;
        const itens = linha.itens.map((item) =>
          item.tipo_periferico_id === tipo.id ? { ...item, entregue } : item
        );
        const entregues = itens.filter((i) => i.entregue).length;
        return { ...linha, itens, entregues, completo: entregues === linha.total };
      })
    );
    setSalvando((s) => new Set(s).add(chave));

    try {
      await checklistService.marcar(colaborador.id, tipo.id, {
        entregue,
        marcadoPor: OPERADOR_ATUAL,
      });
      carregarSetores();
    } catch (e) {
      // Falhou: volta ao estado real do servidor em vez de mentir na tela.
      setLinhas(anterior);
      setErro(`Não foi possível salvar ${tipo.nome} de ${colaborador.nome}. ${e.message}`);
    } finally {
      setSalvando((s) => {
        const proximo = new Set(s);
        proximo.delete(chave);
        return proximo;
      });
    }
  }

  const geral = useMemo(() => {
    const entregues = setores.reduce((soma, s) => soma + s.itens_entregues, 0);
    const previstos = setores.reduce((soma, s) => soma + s.itens_previstos, 0);
    const pessoas = setores.reduce((soma, s) => soma + s.total_colaboradores, 0);
    const completos = setores.reduce((soma, s) => soma + s.colaboradores_completos, 0);
    return { entregues, previstos, pessoas, completos };
  }, [setores]);

  return (
    <div className="chk">
      <header className="chk-topo">
        <div>
          <h1 className="chk-titulo">Checklist de periféricos</h1>
          <p className="chk-sub">
            {geral.completos} de {geral.pessoas} colaboradores com todos os{" "}
            {tipos.length || 7} itens entregues
          </p>
        </div>
        <div className="chk-medidor" aria-hidden="true">
          <div className="chk-medidor-num">
            {geral.previstos ? Math.round((geral.entregues / geral.previstos) * 100) : 0}
            <span>%</span>
          </div>
          <div className="chk-medidor-txt">
            {geral.entregues} de {geral.previstos} itens
          </div>
        </div>
      </header>

      {erro && (
        <div className="chk-erro" role="alert">
          <span>{erro}</span>
          <button type="button" onClick={carregarLinhas}>
            Tentar de novo
          </button>
        </div>
      )}

      <div className="chk-corpo">
        <nav className="chk-setores" aria-label="Filtrar por setor">
          <button
            type="button"
            className={`chk-setor ${setorAtivo === null ? "esta-ativo" : ""}`}
            onClick={() => setSetorAtivo(null)}
          >
            <span className="chk-setor-nome">Todos os setores</span>
            <span className="chk-setor-num">{geral.pessoas}</span>
          </button>

          {setores.map((setor) => (
            <button
              key={setor.id}
              type="button"
              className={`chk-setor ${setorAtivo === setor.id ? "esta-ativo" : ""}`}
              onClick={() => setSetorAtivo(setor.id)}
            >
              <span className="chk-setor-nome">{setor.nome}</span>
              <span className="chk-setor-num">{setor.total_colaboradores}</span>
              <span className="chk-barra">
                <span
                  className="chk-barra-preenchida"
                  style={{ width: `${setor.percentual}%` }}
                />
              </span>
            </button>
          ))}
        </nav>

        <section className="chk-painel">
          <div className="chk-filtros">
            <input
              type="search"
              className="chk-busca"
              placeholder="Buscar por nome ou e-mail"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              aria-label="Buscar colaborador"
            />
            <label className="chk-toggle">
              <input
                type="checkbox"
                checked={apenasPendentes}
                onChange={(e) => setApenasPendentes(e.target.checked)}
              />
              Só quem tem pendência
            </label>
            <span className="chk-contagem">{total} colaboradores</span>
          </div>

          <div className="chk-rolagem">
            <table className="chk-tabela">
              <thead>
                <tr>
                  <th scope="col" className="chk-col-nome">
                    Colaborador
                  </th>
                  {tipos.map((tipo) => (
                    <th key={tipo.id} scope="col" className="chk-col-item">
                      <abbr title={tipo.nome}>{abreviar(tipo.nome)}</abbr>
                    </th>
                  ))}
                  <th scope="col" className="chk-col-prog">
                    Entregue
                  </th>
                </tr>
              </thead>
              <tbody>
                {linhas.map((linha) => (
                  <tr key={linha.id} className={linha.completo ? "esta-completo" : ""}>
                    <th scope="row" className="chk-col-nome">
                      <span className="chk-pessoa">{linha.nome}</span>
                      <span className="chk-email">{linha.email}</span>
                      {!setorAtivo && linha.centro_custo && (
                        <span className="chk-tag">{linha.centro_custo.nome}</span>
                      )}
                    </th>

                    {tipos.map((tipo) => {
                      const item = linha.itens.find(
                        (i) => i.tipo_periferico_id === tipo.id
                      );
                      const chave = `${linha.id}:${tipo.id}`;
                      return (
                        <td key={tipo.id} className="chk-col-item">
                          <input
                            type="checkbox"
                            className="chk-caixa"
                            checked={item?.entregue ?? false}
                            disabled={salvando.has(chave)}
                            onChange={(e) => alternar(linha, tipo, e.target.checked)}
                            aria-label={`${tipo.nome} de ${linha.nome}`}
                          />
                        </td>
                      );
                    })}

                    <td className="chk-col-prog">
                      <span className="chk-fracao">
                        {linha.entregues}/{linha.total}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {!carregando && linhas.length === 0 && (
              <p className="chk-vazio">
                {buscaAplicada
                  ? `Nenhum colaborador encontrado para "${buscaAplicada}".`
                  : apenasPendentes
                    ? "Todo mundo deste filtro está com os periféricos completos."
                    : "Nenhum colaborador cadastrado neste setor. Rode a sincronização com o GLPI."}
              </p>
            )}

            {carregando && <p className="chk-vazio">Carregando…</p>}
          </div>
        </section>
      </div>
    </div>
  );
}
