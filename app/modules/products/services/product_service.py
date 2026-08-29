from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.products.exceptions.product_exceptions import (
    InvalidCategoryError,
    ProductNotFoundError,
    SkuAlreadyExistsError,
)
from app.modules.products.models.product import Product
from app.modules.products.repositories.product_repository import ProductRepository
from app.shared.enums.product_status import ProductStatus
from app.shared.utils.slugify import slugify


class ProductService:

    def __init__(self, repository: ProductRepository, category_repository: CategoryRepository) -> None:
        self.repository = repository
        self.category_repository = category_repository

    async def _validate_category(self, category_id: int) -> None:
        category = await self.category_repository.get_by_id(category_id)
        if category is None or not category.is_active:
            raise InvalidCategoryError(category_id)

    async def _unique_slug_for(self, name: str) -> str:
        base_slug = slugify(name)
        candidate = base_slug
        suffix = 2
        while await self.repository.get_by_slug(candidate) is not None:
            candidate = f"{base_slug}-{suffix}"
            suffix += 1
        return candidate

    async def create_product(
        self,
        *,
        name: str,
        description: str | None,
        price_cents: int,
        sku: str,
        stock: int,
        category_id: int,
        status: ProductStatus,
    ) -> Product:
        await self._validate_category(category_id)

        if await self.repository.get_by_sku(sku) is not None:
            raise SkuAlreadyExistsError(sku)

        slug = await self._unique_slug_for(name)

        return await self.repository.create(
            name=name,
            slug=slug,
            description=description,
            price_cents=price_cents,
            sku=sku,
            stock=stock,
            category_id=category_id,
            status=status,
        )

    async def get_product(self, product_id: int) -> Product:
        product = await self.repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return product

    async def list_products(self, *, offset: int, limit: int) -> tuple[list[Product], int]:
        return await self.repository.list_paginated(offset=offset, limit=limit)

    async def update_product(
        self,
        *,
        product_id: int,
        name: str | None,
        description: str | None,
        price_cents: int | None,
        stock: int | None,
        category_id: int | None,
        status: ProductStatus | None,
    ) -> Product:
        product = await self.repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)

        updates: dict = {}

        if category_id is not None:
            await self._validate_category(category_id)
            updates["category_id"] = category_id

        if name is not None and name != product.name:
            updates["name"] = name
            updates["slug"] = await self._unique_slug_for(name)

        if description is not None:
            updates["description"] = description
        if price_cents is not None:
            updates["price_cents"] = price_cents
        if stock is not None:
            updates["stock"] = stock
        if status is not None:
            updates["status"] = status

        return await self.repository.update(product, **updates)

    async def archive_product(self, product_id: int) -> Product:

        product = await self.repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return await self.repository.update(product, status=ProductStatus.ARCHIVED)
