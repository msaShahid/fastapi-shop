from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums.product_status import ProductStatus
from app.shared.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.modules.categories.models.category import Category

class Product(Base, TimestampMixin):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    price_cents: Mapped[int] = mapped_column(Integer)

    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    status: Mapped[ProductStatus] = mapped_column(
        Enum(
            ProductStatus,
            name="product_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=ProductStatus.DRAFT,
        server_default=ProductStatus.DRAFT.value,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        index=True,
    )
    # category is the parent of the product
    category: Mapped["Category"] = relationship(back_populates="products")

    __table_args__ = (
        CheckConstraint("price_cents > 0", name="ck_products_price_positive"),
        CheckConstraint("stock >= 0", name="ck_products_stock_non_negative"),
    )
