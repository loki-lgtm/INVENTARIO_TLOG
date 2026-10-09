from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.colaborador import Colaborador


class CentroCusto(Base, TimestampMixin):
    """Um departamento/setor da empresa (Comercial, TI, Financeiro...).

    `gestor_id` aponta para o colaborador responsável pelo setor: é quem
    assina o termo como gestor no envelope do DocuSign, e também alimenta o
    modal de gestores por departamento do Dashboard.
    """

    __tablename__ = "centros_custo"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    gestor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("colaboradores.id", use_alter=True, name="fk_centro_custo_gestor")
    )

    gestor: Mapped[Optional["Colaborador"]] = relationship(foreign_keys=[gestor_id])
    colaboradores: Mapped[list["Colaborador"]] = relationship(
        back_populates="centro_custo", foreign_keys="Colaborador.centro_custo_id"
    )

    def __repr__(self) -> str:
        return f"<CentroCusto {self.nome}>"
