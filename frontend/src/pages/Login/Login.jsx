import { useState } from "react";
import TlogMark from "../../components/brand/TlogMark.jsx";
import "./Login.css";

const DEPARTAMENTOS = [
  "Comercial",
  "Administrativo",
  "Manutenção",
  "TI",
  "Financeiro",
  "Contratos",
  "Controladoria",
];

const ABA_ACESSO = "acesso";
const ABA_SOLICITAR = "solicitar";

// Tela de autenticação: ainda não existe backend de auth, então todo envio
// aqui é local — só confirma pro usuário que o formulário funciona.
export default function Login() {
  const [aba, setAba] = useState(ABA_ACESSO);
  const [mensagem, setMensagem] = useState(null);

  const [acesso, setAcesso] = useState({ usuario: "", senha: "", lembrar: false });
  const [solicitacao, setSolicitacao] = useState({
    email: "",
    login: "",
    cargo: "",
    departamento: DEPARTAMENTOS[0],
  });

  function trocarAba(proxima) {
    setAba(proxima);
    setMensagem(null);
  }

  function enviarAcesso(e) {
    e.preventDefault();
    setMensagem("Protótipo sem backend: nenhuma autenticação foi enviada.");
  }

  function enviarSolicitacao(e) {
    e.preventDefault();
    setMensagem("Protótipo sem backend: a solicitação não foi enviada de verdade.");
  }

  function esqueciSenha(e) {
    e.preventDefault();
    setMensagem("Protótipo sem backend: recuperação de senha ainda não existe.");
  }

  return (
    <div className="lg">
      <div className="lg-cartao">
        <div className="lg-hero">
          <div className="lg-hero-lockup">
            <TlogMark size={56} />
            <span className="lg-hero-divisor" aria-hidden="true" />
            <span className="lg-hero-wordmark">
              <span className="g">GRUPO</span>
              <span className="t">TLOG</span>
            </span>
          </div>
          <p className="lg-hero-tagline">Torre de Controle — Gestão de TI</p>
          <span className="lg-hero-rodape">Acesso restrito a colaboradores do Grupo TLOG</span>
        </div>

        <div className="lg-corpo">
          <div className="lg-abas" role="tablist" aria-label="Formulário de acesso">
            <button
              type="button"
              role="tab"
              aria-selected={aba === ABA_ACESSO}
              className={`lg-aba ${aba === ABA_ACESSO ? "esta-ativa" : ""}`}
              onClick={() => trocarAba(ABA_ACESSO)}
            >
              Acesso
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={aba === ABA_SOLICITAR}
              className={`lg-aba ${aba === ABA_SOLICITAR ? "esta-ativa" : ""}`}
              onClick={() => trocarAba(ABA_SOLICITAR)}
            >
              Solicitar Acesso
            </button>
          </div>

          {mensagem && (
            <p className="lg-mensagem" role="status">
              {mensagem}
            </p>
          )}

          {aba === ABA_ACESSO ? (
            <form className="lg-form" onSubmit={enviarAcesso}>
            <label className="lg-campo">
              <span>Usuário</span>
              <input
                type="text"
                value={acesso.usuario}
                onChange={(e) => setAcesso({ ...acesso, usuario: e.target.value })}
                autoComplete="username"
                required
              />
            </label>

            <label className="lg-campo">
              <span>Senha</span>
              <input
                type="password"
                value={acesso.senha}
                onChange={(e) => setAcesso({ ...acesso, senha: e.target.value })}
                autoComplete="current-password"
                required
              />
            </label>

            <div className="lg-linha-extra">
              <label className="lg-lembrar">
                <input
                  type="checkbox"
                  checked={acesso.lembrar}
                  onChange={(e) => setAcesso({ ...acesso, lembrar: e.target.checked })}
                />
                Lembrar de mim
              </label>
              <button type="button" className="lg-link" onClick={esqueciSenha}>
                Esqueci a senha
              </button>
            </div>

            <button type="submit" className="lg-botao">
              Entrar
            </button>
          </form>
        ) : (
          <form className="lg-form" onSubmit={enviarSolicitacao}>
            <label className="lg-campo">
              <span>E-mail corporativo</span>
              <input
                type="email"
                value={solicitacao.email}
                onChange={(e) => setSolicitacao({ ...solicitacao, email: e.target.value })}
                autoComplete="email"
                required
              />
            </label>

            <label className="lg-campo">
              <span>Login</span>
              <input
                type="text"
                value={solicitacao.login}
                onChange={(e) => setSolicitacao({ ...solicitacao, login: e.target.value })}
                required
              />
            </label>

            <label className="lg-campo">
              <span>Cargo</span>
              <input
                type="text"
                value={solicitacao.cargo}
                onChange={(e) => setSolicitacao({ ...solicitacao, cargo: e.target.value })}
                required
              />
            </label>

            <label className="lg-campo">
              <span>Departamento</span>
              <select
                value={solicitacao.departamento}
                onChange={(e) =>
                  setSolicitacao({ ...solicitacao, departamento: e.target.value })
                }
              >
                {DEPARTAMENTOS.map((dep) => (
                  <option key={dep} value={dep}>
                    {dep}
                  </option>
                ))}
              </select>
            </label>

            <button type="submit" className="lg-botao">
              Enviar solicitação
            </button>
          </form>
          )}
        </div>
      </div>
    </div>
  );
}
