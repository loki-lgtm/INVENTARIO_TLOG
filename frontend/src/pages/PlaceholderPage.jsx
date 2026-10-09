import { useLocation, useParams } from "react-router-dom";
import { DEPARTAMENTOS, SISTEMAS_INTEGRACAO } from "../components/layout/Sidebar.jsx";
import "./PlaceholderPage.css";

const TITULOS_FIXOS = {
  "/compras": "Requisição de Compra",
  "/termos": "Envio de Termos",
  "/relatorios": "Relatórios",
  "/configuracoes": "Configurações",
};

function tituloPadrao(pathname, params) {
  if (params.departamento) {
    const dep = DEPARTAMENTOS.find((d) => d.slug === params.departamento);
    return `Movimentação - ${dep?.nome ?? params.departamento}`;
  }
  if (params.sistema) {
    const sistema = SISTEMAS_INTEGRACAO.find((s) => s.slug === params.sistema);
    return `Integrações - ${sistema?.nome ?? params.sistema}`;
  }
  return TITULOS_FIXOS[pathname] ?? "Módulo";
}

// Placeholder genérico para rotas que ainda não têm tela própria.
// Aceita um título fixo via prop; sem ele, deriva da URL (útil pras rotas com parâmetro).
export default function PlaceholderPage({ titulo }) {
  const location = useLocation();
  const params = useParams();
  const tituloFinal = titulo ?? tituloPadrao(location.pathname, params);

  return (
    <div className="ph">
      <div className="ph-cartao">
        <h1 className="ph-titulo">{tituloFinal}</h1>
        <p className="ph-texto">Este módulo ainda está em construção.</p>
      </div>
    </div>
  );
}
