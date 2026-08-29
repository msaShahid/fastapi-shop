from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models.category import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self.db.get(Category, category_id)

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def list_paginated(
        self, *, offset: int, limit: int
    ) -> tuple[list[Category], int]:
        total_result = await self.db.execute(select(func.count()).select_from(Category))
        total = total_result.scalar_one()

        items_result = await self.db.execute(
            select(Category).order_by(Category.name).offset(offset).limit(limit)
        )
        items = list(items_result.scalars().all())

        return items, total

    async def create(
        self, *, name: str, slug: str, description: str | None
    ) -> Category:
        category = Category(name=name, slug=slug, description=description)
        self.db.add(category)
        await self.db.flush()
        return category

    async def update(self, category: Category, **fields) -> Category:
        for key, value in fields.items():
            setattr(category, key, value)
        await self.db.flush()
        return category

    async def deactivate(self, category: Category) -> Category:
        category.is_active = False
        await self.db.flush()
        return category
