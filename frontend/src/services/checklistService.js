import { api } from "./api";

function montarQuery({ centroCustoId, busca, apenasPendentes } = {}) {
  const params = new URLSearchParams();
  if (centroCustoId != null) params.set("centro_custo_id", centroCustoId);
  if (busca) params.set("busca", busca);
  if (apenasPendentes) params.set("apenas_pendentes", "true");
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const checklistService = {
  listarSetores: () => api.get("/checklist/setores"),

  listar: (filtros) => api.get(`/checklist${montarQuery(filtros)}`),

  marcar: (colaboradorId, tipoId, { entregue, marcadoPor, observacao }) =>
    api.put(`/checklist/${colaboradorId}/${tipoId}`, {
      entregue,
      marcado_por: marcadoPor,
      observacao,
    }),
};
