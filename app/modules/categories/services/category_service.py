from app.modules.categories.exceptions.category_exceptions import (
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
)
from app.modules.categories.models.category import Category
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.shared.utils.slugify import slugify


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def _unique_slug_for(self, name: str) -> str:

        base_slug = slugify(name)
        candidate = base_slug
        suffix = 2
        while await self.repository.get_by_slug(candidate) is not None:
            candidate = f"{base_slug}-{suffix}"
            suffix += 1
        return candidate

    async def create_category(self, *, name: str, description: str | None) -> Category:
        if await self.repository.get_by_name(name) is not None:
            raise CategoryNameAlreadyExistsError(name)

        slug = await self._unique_slug_for(name)
        return await self.repository.create(name=name, slug=slug, description=description)

    async def get_category(self, category_id: int) -> Category:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)
        return category

    async def list_categories(self, *, offset: int, limit: int) -> tuple[list[Category], int]:
        return await self.repository.list_paginated(offset=offset, limit=limit)

    async def update_category(
        self,
        *,
        category_id: int,
        name: str | None,
        description: str | None,
        is_active: bool | None,
    ) -> Category:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)

        updates: dict = {}

        if name is not None and name != category.name:
            if await self.repository.get_by_name(name) is not None:
                raise CategoryNameAlreadyExistsError(name)
            updates["name"] = name

            updates["slug"] = await self._unique_slug_for(name)

        if description is not None:
            updates["description"] = description

        if is_active is not None:
            updates["is_active"] = is_active

        return await self.repository.update(category, **updates)

    async def deactivate_category(self, category_id: int) -> Category:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)
        return await self.repository.deactivate(category)
