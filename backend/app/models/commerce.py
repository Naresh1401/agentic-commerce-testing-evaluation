from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductRecord(Base):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String, primary_key=True)
    upc: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    brand: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    size: Mapped[str] = mapped_column(String)
    base_price: Mapped[float] = mapped_column(Float)


class InventoryRecord(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String, index=True)
    store_id: Mapped[str] = mapped_column(String, index=True)
    quantity_available: Mapped[int] = mapped_column(Integer)
