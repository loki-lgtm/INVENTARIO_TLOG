from typing import Optional

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ItemEstoque(Base, TimestampMixin):
    """Um tipo de equipamento controlado em estoque (Notebook, Teclado, Mouse...).

    É o catálogo, não a unidade física — a quantidade por setor e estado de
    conservação vive em `EstoqueSetor`. `alerta_minimo` é o piso abaixo do
    qual o saldo de um setor é sinalizado na tela.
    """

    __tablename__ = "itens_estoque"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    categoria: Mapped[Optional[str]] = mapped_column(String(80))
    alerta_minimo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<ItemEstoque {self.nome}>"
