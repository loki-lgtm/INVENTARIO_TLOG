from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.centro_custo import CentroCusto
    from app.models.checklist import ChecklistItem


class Colaborador(Base, TimestampMixin):
    """Um funcionário da empresa: alvo de checklist, termos e equipamentos entregues."""

    __tablename__ = "colaboradores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(180), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    cargo: Mapped[Optional[str]] = mapped_column(String(120))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    centro_custo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("centros_custo.id"))

    centro_custo: Mapped[Optional["CentroCusto"]] = relationship(
        back_populates="colaboradores", foreign_keys=[centro_custo_id]
    )
    checklist: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="colaborador", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Colaborador {self.nome}>"
