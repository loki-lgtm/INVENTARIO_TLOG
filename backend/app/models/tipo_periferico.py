from typing import Optional

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class TipoPeriferico(Base, TimestampMixin):
    """Um tipo de periférico entregável (Mouse, Teclado, Hub USB...).

    Deliberadamente uma tabela e não colunas booleanas fixas: a lista do
    termo de responsabilidade já passou de 5 para 7 itens antes do sistema
    existir. Como tabela, incluir um novo periférico é inserir uma linha —
    sem migração de banco, sem mexer em schema, rota ou tela.

    `ativo=False` aposenta um periférico sem apagar o histórico de quem já
    recebeu aquele item.
    """

    __tablename__ = "tipos_periferico"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observacao: Mapped[Optional[str]] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<TipoPeriferico {self.nome}>"
