import pytest
from app.shared.enums.product_status import ProductStatus

from app.modules.products.exceptions.product_exceptions import (
    InvalidCategoryError,
    ProductNotFoundError,
    SkuAlreadyExistsError,
)
from app.modules.products.services.product_service import ProductService


@pytest.fixture
def product_service(fake_product_repository, fake_category_repository_for_products) -> ProductService:
    return ProductService(fake_product_repository, fake_category_repository_for_products)


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
    """
    Category 2 EXISTS but is inactive -- this is the case that a naive
    "does category_id exist" check would miss. Products shouldn't be
    assignable to a category that's been deactivated, even though the
    category row itself is still there.
    """
    with pytest.raises(InvalidCategoryError):
        await _make_product(product_service, category_id=2, sku="X-002")


async def test_create_product_rejects_duplicate_sku(product_service):
    await _make_product(product_service, sku="DUP-001")
    with pytest.raises(SkuAlreadyExistsError):
        await _make_product(product_service, name="Different Name", sku="DUP-001")


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
