from datetime import UTC, datetime, timedelta

import pytest

from app.modules.products.exceptions.product_exceptions import (
    InvalidCategoryError,
    ProductNotFoundError,
)
from app.modules.products.models.product import Product
from app.modules.products.services.product_service import ProductService
from app.shared.enums.product_status import ProductStatus


@pytest.fixture
def product_service(
    fake_product_repository, fake_category_repository_for_products
) -> ProductService:
    return ProductService(
        fake_product_repository, fake_category_repository_for_products
    )


async def _make_product(service, **overrides):
    defaults = dict(
        name="Wireless Mouse",
        description=None,
        price_cents=1999,
        sku="MOUSE-001",
        stock=10,
        category_id=1,
        status=ProductStatus.ACTIVE,
    )
    defaults.update(overrides)
    return await service.create_product(**defaults)


async def test_create_product_with_valid_category_succeeds(product_service):
    product = await _make_product(product_service)
    assert product.category_id == 1
    assert product.slug == "wireless-mouse"


async def test_create_product_with_nonexistent_category_rejected(product_service):
    with pytest.raises(InvalidCategoryError):
        await _make_product(product_service, category_id=999, sku="X-001")


async def test_create_product_with_inactive_category_rejected(product_service):

    with pytest.raises(InvalidCategoryError):
        await _make_product(product_service, category_id=2, sku="X-002")


async def create(self, **fields) -> Product:

    fake_created_at = datetime(2024, 1, 1, tzinfo=UTC) + timedelta(
        seconds=self._next_id
    )
    product = Product(
        id=self._next_id,
        created_at=fields.pop("created_at", fake_created_at),
        updated_at=fields.pop("updated_at", fake_created_at),
        **fields,
    )
    self.products[self._next_id] = product
    self._next_id += 1
    return product


async def test_get_nonexistent_product_raises_not_found(product_service):
    with pytest.raises(ProductNotFoundError):
        await product_service.get_product(9999)


async def test_update_product_category_revalidates_it(product_service):
    product = await _make_product(product_service)

    with pytest.raises(InvalidCategoryError):
        await product_service.update_product(
            product_id=product.id,
            name=None,
            description=None,
            price_cents=None,
            stock=None,
            category_id=2,  # inactive
            status=None,
        )


async def test_update_product_price_and_stock(product_service):
    product = await _make_product(product_service)

    updated = await product_service.update_product(
        product_id=product.id,
        name=None,
        description=None,
        price_cents=2999,
        stock=5,
        category_id=None,
        status=None,
    )

    assert updated.price_cents == 2999
    assert updated.stock == 5


async def test_archive_product_sets_status_archived(product_service):
    product = await _make_product(product_service)

    archived = await product_service.archive_product(product.id)

    assert archived.status == ProductStatus.ARCHIVED

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        category_id: int | None = None,
        search: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        sort: str = "-created_at",
    ) -> tuple[list[Product], int]:
        results = list(self.products.values())

        if category_id is not None:
            results = [p for p in results if p.category_id == category_id]
        if search:
            results = [p for p in results if search.lower() in p.name.lower()]
        if min_price is not None:
            results = [p for p in results if p.price_cents >= min_price]
        if max_price is not None:
            results = [p for p in results if p.price_cents <= max_price]

        is_descending = sort.startswith("-")
        sort_key = sort.lstrip("-")
        results.sort(key=lambda p: getattr(p, sort_key), reverse=is_descending)

        total = len(results)
        return results[offset : offset + limit], total
