import { Route, Routes } from "react-router-dom";
import Layout from "./components/layout/Layout.jsx";
import Dashboard from "./pages/Dashboard/Dashboard.jsx";
import Checklist from "./pages/Checklist/Checklist.jsx";
import EstoquePorSetor from "./pages/EstoquePorSetor/EstoquePorSetor.jsx";
import PlaceholderPage from "./pages/PlaceholderPage.jsx";
import Login from "./pages/Login/Login.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/checklist" element={<Checklist />} />
        <Route path="/estoque" element={<EstoquePorSetor />} />
        <Route path="/movimentacao/:departamento" element={<PlaceholderPage />} />
        <Route path="/compras" element={<PlaceholderPage />} />
        <Route path="/relatorios" element={<PlaceholderPage />} />
        <Route path="/termos" element={<PlaceholderPage />} />
        <Route path="/integracoes/:sistema" element={<PlaceholderPage />} />
        <Route path="/configuracoes" element={<PlaceholderPage />} />
      </Route>
    </Routes>
  );
}
