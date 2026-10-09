from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.colaborador import Colaborador
    from app.models.tipo_periferico import TipoPeriferico


class ChecklistItem(Base, TimestampMixin):
    """Entrega de um periférico a um colaborador.

    Substitui o antigo `data.json` e a tabela `equipamentos_entregues` de
    colunas fixas. Uma linha por colaborador x periférico.

    `marcado_por` guarda quem operou a marcação. É o que permite auditar uma
    divergência de inventário depois — sem isso, o checklist diz o que foi
    entregue mas não quem afirmou isso.
    """

    __tablename__ = "checklist_itens"
    __table_args__ = (
        UniqueConstraint(
            "colaborador_id", "tipo_periferico_id", name="uq_checklist_colaborador_tipo"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    colaborador_id: Mapped[int] = mapped_column(
        ForeignKey("colaboradores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_periferico_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_periferico.id", ondelete="CASCADE"), nullable=False, index=True
    )

    entregue: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_entrega: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    marcado_por: Mapped[Optional[str]] = mapped_column(String(180))
    observacao: Mapped[Optional[str]] = mapped_column(String(255))

    colaborador: Mapped["Colaborador"] = relationship(back_populates="checklist")
    tipo_periferico: Mapped["TipoPeriferico"] = relationship()

    def __repr__(self) -> str:
        return f"<ChecklistItem c={self.colaborador_id} t={self.tipo_periferico_id} {self.entregue}>"
