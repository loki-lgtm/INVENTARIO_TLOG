import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar.jsx";
import "./Layout.css";

// Casca das rotas autenticadas: sidebar fixa + área de conteúdo rolável.
export default function Layout() {
  return (
    <div className="lay">
      <Sidebar />
      <main className="lay-conteudo">
        <Outlet />
      </main>
    </div>
  );
}
