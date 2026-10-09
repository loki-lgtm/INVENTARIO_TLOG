import { Link } from "react-router-dom";
import TlogMark from "../../components/brand/TlogMark.jsx";
import "./Dashboard.css";

const MODULOS = [
  { nome: "Checklist", descricao: "Entrega de periféricos por colaborador.", to: "/checklist" },
  { nome: "Estoque por Setor", descricao: "Itens disponíveis em cada centro de custo.", to: "/estoque" },
  { nome: "Movimentação", descricao: "Entrada e saída de equipamentos por departamento.", to: "/movimentacao/ti" },
  { nome: "Requisição de Compra", descricao: "Pedidos de compra de equipamentos.", to: "/compras" },
  { nome: "Envio de Termos", descricao: "Termos de responsabilidade para assinatura.", to: "/termos" },
  { nome: "Relatórios", descricao: "Indicadores e exportações do inventário.", to: "/relatorios" },
];

export default function Dashboard() {
  return (
    <div className="dash">
      <header className="dash-topo">
        <TlogMark size={36} />
        <div>
          <h1 className="dash-titulo">Grupo TLOG</h1>
          <p className="dash-sub">
            Torre de Controle — bem-vindo(a). Escolha um módulo abaixo para começar.
          </p>
        </div>
      </header>

      <div className="dash-grade">
        {MODULOS.map((modulo) => (
          <Link key={modulo.nome} to={modulo.to} className="dash-cartao">
            <strong className="dash-cartao-nome">{modulo.nome}</strong>
            <span className="dash-cartao-desc">{modulo.descricao}</span>
            {modulo.nome !== "Checklist" && modulo.nome !== "Estoque por Setor" && (
              <span className="dash-cartao-tag">em construção</span>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
