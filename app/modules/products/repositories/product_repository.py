from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models.product import Product


class ProductRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.db.get(Product, product_id)

    async def get_by_sku(self, sku: str) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.sku == sku))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.slug == slug))
        return result.scalar_one_or_none()

    async def list_paginated(self, *, offset: int, limit: int) -> tuple[list[Product], int]:
 
        total_result = await self.db.execute(select(func.count()).select_from(Product))
        total = total_result.scalar_one()

        items_result = await self.db.execute(
            select(Product).order_by(Product.created_at.desc()).offset(offset).limit(limit)
        )
        items = list(items_result.scalars().all())

        return items, total

    async def create(self, **fields) -> Product:
        product = Product(**fields)
        self.db.add(product)
        await self.db.flush()
        return product

    async def update(self, product: Product, **fields) -> Product:
        for key, value in fields.items():
            setattr(product, key, value)
        await self.db.flush()
        return product
