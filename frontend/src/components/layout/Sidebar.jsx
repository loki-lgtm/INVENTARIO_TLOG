import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import TlogMark from "../brand/TlogMark.jsx";
import "./Sidebar.css";

// Enquanto não existe autenticação, os dados do rodapé são fixos.
const USUARIO_ATUAL = { iniciais: "EB", nome: "Eduardo B.", cargo: "Suporte de TI" };

// Exportados para reuso em PlaceholderPage, que monta o título a partir do slug da URL.
export const DEPARTAMENTOS = [
  { slug: "comercial", nome: "Comercial" },
  { slug: "administrativo", nome: "Administrativo" },
  { slug: "manutencao", nome: "Manutenção" },
  { slug: "ti", nome: "TI" },
  { slug: "financeiro", nome: "Financeiro" },
  { slug: "contratos", nome: "Contratos" },
  { slug: "controladoria", nome: "Controladoria" },
];

export const SISTEMAS_INTEGRACAO = [
  { slug: "glpi", nome: "GLPI" },
  { slug: "docusign", nome: "DocuSign" },
];

function abreviar(nome) {
  const palavras = nome.split(" ").filter(Boolean);
  if (palavras.length === 1) return palavras[0].slice(0, 2).toUpperCase();
  return palavras
    .slice(0, 2)
    .map((p) => p[0])
    .join("")
    .toUpperCase();
}

function ItemLink({ to, nome, recolhida }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `sb-item ${isActive ? "esta-ativo" : ""}`}
      title={recolhida ? nome : undefined}
    >
      <span className="sb-item-marca" aria-hidden="true">
        {abreviar(nome)}
      </span>
      <span className="sb-item-texto">{nome}</span>
    </NavLink>
  );
}

function GrupoExpansivel({ nome, aberto, ativo, recolhida, onToggle, children }) {
  return (
    <div className="sb-grupo">
      <button
        type="button"
        className={`sb-item sb-grupo-cabeca ${ativo ? "esta-ativo" : ""}`}
        onClick={onToggle}
        title={recolhida ? nome : undefined}
        aria-expanded={aberto}
      >
        <span className="sb-item-marca" aria-hidden="true">
          {abreviar(nome)}
        </span>
        <span className="sb-item-texto">{nome}</span>
        <span className={`sb-seta ${aberto ? "esta-aberta" : ""}`} aria-hidden="true">
          ›
        </span>
      </button>
      {aberto && !recolhida && <div className="sb-sublista">{children}</div>}
    </div>
  );
}

export default function Sidebar() {
  const location = useLocation();
  const [recolhida, setRecolhida] = useState(false);

  const emMovimentacao =
    location.pathname.startsWith("/movimentacao") || location.pathname.startsWith("/estoque");
  const emIntegracoes = location.pathname.startsWith("/integracoes");

  const [movimentacaoAberta, setMovimentacaoAberta] = useState(emMovimentacao);
  const [integracoesAberta, setIntegracoesAberta] = useState(emIntegracoes);

  // Abre automaticamente o grupo correspondente ao navegar direto para uma sub-rota.
  useEffect(() => {
    if (emMovimentacao) setMovimentacaoAberta(true);
  }, [emMovimentacao]);

  useEffect(() => {
    if (emIntegracoes) setIntegracoesAberta(true);
  }, [emIntegracoes]);

  function alternarGrupo(aberto, setAberto) {
    if (recolhida) {
      // Com a barra recolhida não há espaço pra sublista: expande a barra e o grupo juntos.
      setRecolhida(false);
      setAberto(true);
      return;
    }
    setAberto(!aberto);
  }

  return (
    <aside className={`sb ${recolhida ? "esta-recolhida" : ""}`}>
      <div className="sb-topo">
        <div className="sb-marca">
          <span className="sb-logo">
            <TlogMark size={32} />
          </span>
          <div className="sb-marca-texto">
            <strong>Grupo TLOG</strong>
            <span>Torre de Controle</span>
          </div>
        </div>
        <button
          type="button"
          className="sb-recolher"
          onClick={() => setRecolhida((v) => !v)}
          aria-label={recolhida ? "Expandir menu" : "Recolher menu"}
          title={recolhida ? "Expandir menu" : "Recolher menu"}
        >
          {recolhida ? "»" : "«"}
        </button>
      </div>

      <nav className="sb-nav" aria-label="Navegação principal">
        <ItemLink to="/" nome="Página Inicial" recolhida={recolhida} />

        <p className="sb-secao-titulo">Equipamentos</p>
        <ItemLink to="/checklist" nome="Checklist" recolhida={recolhida} />

        <GrupoExpansivel
          nome="Movimentação"
          aberto={movimentacaoAberta}
          ativo={emMovimentacao}
          recolhida={recolhida}
          onToggle={() => alternarGrupo(movimentacaoAberta, setMovimentacaoAberta)}
        >
          {DEPARTAMENTOS.map((dep) => (
            <ItemLink
              key={dep.slug}
              to={`/movimentacao/${dep.slug}`}
              nome={dep.nome}
              recolhida={recolhida}
            />
          ))}
          <ItemLink to="/estoque" nome="Estoque" recolhida={recolhida} />
        </GrupoExpansivel>

        <p className="sb-secao-titulo">Compras &amp; Documentos</p>
        <ItemLink to="/compras" nome="Requisição de Compra" recolhida={recolhida} />
        <ItemLink to="/termos" nome="Envio de Termos" recolhida={recolhida} />
        <ItemLink to="/relatorios" nome="Relatórios" recolhida={recolhida} />

        <p className="sb-secao-titulo">Sistema</p>
        <GrupoExpansivel
          nome="Integrações"
          aberto={integracoesAberta}
          ativo={emIntegracoes}
          recolhida={recolhida}
          onToggle={() => alternarGrupo(integracoesAberta, setIntegracoesAberta)}
        >
          <ItemLink to="/integracoes/glpi" nome="GLPI" recolhida={recolhida} />
          <ItemLink to="/integracoes/docusign" nome="DocuSign" recolhida={recolhida} />
        </GrupoExpansivel>
        <ItemLink to="/configuracoes" nome="Configurações" recolhida={recolhida} />
      </nav>

      <div className="sb-rodape">
        <span className="sb-avatar" aria-hidden="true">
          {USUARIO_ATUAL.iniciais}
        </span>
        <div className="sb-rodape-texto">
          <strong>{USUARIO_ATUAL.nome}</strong>
          <span>{USUARIO_ATUAL.cargo}</span>
        </div>
      </div>
    </aside>
  );
}
