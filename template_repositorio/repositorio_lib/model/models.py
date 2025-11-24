"""
Modelos SQLAlchemy

Este archivo debe ser generado con sqlacodegen:
sqlacodegen postgresql+psycopg2://user:pass@host:port/db > repositorio_lib/model/models.py

TODO: Generar modelos desde tu base de datos
"""

from typing import Optional

from sqlalchemy import (
    Boolean,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TblBase(Base):
    __tablename__ = "tbl_base"
    __table_args__ = (PrimaryKeyConstraint("bas_id", name="tbl_base_pk"),)

    bas_id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    bas_nombre: Mapped[str] = mapped_column(String)
    bas_activo: Mapped[Optional[bool]] = mapped_column(Boolean)
