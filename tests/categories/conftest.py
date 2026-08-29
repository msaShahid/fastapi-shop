import pytest

from app.modules.categories.models.category import Category


class FakeCategoryRepository:
    def __init__(self) -> None:
        self.categories: dict[int, Category] = {}
        self._next_id = 1

    async def get_by_id(self, category_id: int) -> Category | None:
        return self.categories.get(category_id)

    async def get_by_name(self, name: str) -> Category | None:
        return next((c for c in self.categories.values() if c.name == name), None)

    async def get_by_slug(self, slug: str) -> Category | None:
        return next((c for c in self.categories.values() if c.slug == slug), None)

    async def list_paginated(
        self, *, offset: int, limit: int
    ) -> tuple[list[Category], int]:
        all_categories = sorted(self.categories.values(), key=lambda c: c.name)
        total = len(all_categories)
        return all_categories[offset : offset + limit], total

    async def create(
        self, *, name: str, slug: str, description: str | None
    ) -> Category:
        category = Category(
            id=self._next_id,
            name=name,
            slug=slug,
            description=description,
            is_active=True,
        )
        self.categories[self._next_id] = category
        self._next_id += 1
        return category

    async def update(self, category: Category, **fields) -> Category:
        for key, value in fields.items():
            setattr(category, key, value)
        return category

    async def deactivate(self, category: Category) -> Category:
        category.is_active = False
        return category


@pytest.fixture
def fake_category_repository() -> FakeCategoryRepository:
    return FakeCategoryRepository()
