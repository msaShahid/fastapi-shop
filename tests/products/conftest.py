import pytest

from app.modules.categories.models.category import Category
from app.modules.products.models.product import Product


class FakeProductRepository:
    def __init__(self) -> None:
        self.products: dict[int, Product] = {}
        self._next_id = 1

    async def get_by_id(self, product_id: int) -> Product | None:
        return self.products.get(product_id)

    async def get_by_sku(self, sku: str) -> Product | None:
        return next((p for p in self.products.values() if p.sku == sku), None)

    async def get_by_slug(self, slug: str) -> Product | None:
        return next((p for p in self.products.values() if p.slug == slug), None)

    async def list_paginated(self, *, offset: int, limit: int) -> tuple[list[Product], int]:
        all_products = sorted(self.products.values(), key=lambda p: p.name)
        total = len(all_products)
        return all_products[offset : offset + limit], total

    async def create(self, **fields) -> Product:
        product = Product(id=self._next_id, **fields)
        self.products[self._next_id] = product
        self._next_id += 1
        return product

    async def update(self, product: Product, **fields) -> Product:
        for key, value in fields.items():
            setattr(product, key, value)
        return product


class FakeCategoryRepositoryForProducts:
    """
    A second fake, standing in for CategoryRepository -- this is the
    cross-module dependency ProductService needs. Pre-seeded with a
    couple of categories so product tests have something valid (and
    something inactive) to reference.
    """

    def __init__(self) -> None:
        self.categories: dict[int, Category] = {
            1: Category(id=1, name="Electronics", slug="electronics", is_active=True),
            2: Category(id=2, name="Discontinued", slug="discontinued", is_active=False),
        }

    async def get_by_id(self, category_id: int) -> Category | None:
        return self.categories.get(category_id)


@pytest.fixture
def fake_product_repository() -> FakeProductRepository:
    return FakeProductRepository()


@pytest.fixture
def fake_category_repository_for_products() -> FakeCategoryRepositoryForProducts:
    return FakeCategoryRepositoryForProducts()
