import { api } from "./api";

export const estoqueService = {
  listarItens: () => api.get("/estoque/itens"),

  listarSetores: () => api.get("/estoque/setores"),

  buscarPorSetor: (centroCustoId) => api.get(`/estoque/${centroCustoId}`),

  atualizarSaldo: (centroCustoId, itemEstoqueId, estado, { quantidade, observacao }) =>
    api.put(`/estoque/${centroCustoId}/${itemEstoqueId}/${estado}`, {
      quantidade,
      observacao,
    }),
};
