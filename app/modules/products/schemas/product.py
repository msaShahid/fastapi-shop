from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.enums.product_status import ProductStatus


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    price_cents: int = Field(gt=0, description="Price in cents, e.g. 1999 for $19.99")
    sku: str = Field(min_length=1, max_length=64)
    stock: int = Field(default=0, ge=0)
    category_id: int
    status: ProductStatus = ProductStatus.DRAFT


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    price_cents: int | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    status: ProductStatus | None = None


class ProductRead(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    price_cents: int
    sku: str
    stock: int
    status: ProductStatus
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
