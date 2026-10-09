const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

async function requisitar(caminho, opcoes = {}) {
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    headers: { "Content-Type": "application/json" },
    ...opcoes,
  });

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => null);
    throw new Error(corpo?.detail ?? `Erro ${resposta.status} ao acessar ${caminho}`);
  }

  if (resposta.status === 204) return null;
  return resposta.json();
}

export const api = {
  get: (caminho) => requisitar(caminho),
  put: (caminho, corpo) =>
    requisitar(caminho, { method: "PUT", body: JSON.stringify(corpo) }),
};
