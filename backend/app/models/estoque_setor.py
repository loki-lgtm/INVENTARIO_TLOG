from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.centro_custo import CentroCusto
    from app.models.item_estoque import ItemEstoque


class EstoqueSetor(Base, TimestampMixin):
    """Saldo de um item de estoque em um setor, por estado de conservação.

    A unidade aqui não é (setor, item) — é (setor, item, estado): TI pode ter
    5 mouses novos e 2 defeituosos ao mesmo tempo, cada saldo em sua própria
    linha.
    """

    __tablename__ = "estoque_setor"
    __table_args__ = (
        UniqueConstraint(
            "item_estoque_id", "centro_custo_id", "estado", name="uq_estoque_item_setor_estado"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    item_estoque_id: Mapped[int] = mapped_column(
        ForeignKey("itens_estoque.id", ondelete="CASCADE"), nullable=False, index=True
    )
    centro_custo_id: Mapped[int] = mapped_column(
        ForeignKey("centros_custo.id", ondelete="CASCADE"), nullable=False, index=True
    )

    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    observacao: Mapped[Optional[str]] = mapped_column(String(255))

    item_estoque: Mapped["ItemEstoque"] = relationship()
    centro_custo: Mapped["CentroCusto"] = relationship()

    def __repr__(self) -> str:
        return f"<EstoqueSetor item={self.item_estoque_id} setor={self.centro_custo_id} {self.estado}={self.quantidade}>"
