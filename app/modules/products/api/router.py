from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies.auth import AdminUser
from app.modules.products.dependencies.product_deps import ProductServiceDep
from app.modules.products.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.shared.pagination.schemas import PaginatedResponse, ProductQueryParams

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    payload: ProductCreate,
    service: ProductServiceDep,
    _admin: AdminUser,
) -> ProductRead:
    product = await service.create_product(
        name=payload.name,
        description=payload.description,
        price_cents=payload.price_cents,
        sku=payload.sku,
        stock=payload.stock,
        category_id=payload.category_id,
        status=payload.status,
    )

    return ProductRead.model_validate(product)


@product_router.get(
    "",
    response_model=PaginatedResponse[ProductRead],
)
async def list_products(
    service: ProductServiceDep,
    params: ProductQueryParams = Depends(),
) -> PaginatedResponse[ProductRead]:
    products, total = await service.list_products(
        offset=params.offset,
        limit=params.page_size,
        category_id=params.category_id,
        search=params.search,
        min_price=params.min_price,
        max_price=params.max_price,
        sort=params.sort,
    )

    return PaginatedResponse(
        items=[ProductRead.model_validate(p) for p in products],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@product_router.get(
    "/{product_id}",
    response_model=ProductRead,
)
async def get_product(
    product_id: int,
    service: ProductServiceDep,
) -> ProductRead:
    product = await service.get_product(product_id)

    return ProductRead.model_validate(product)


@product_router.patch(
    "/{product_id}",
    response_model=ProductRead,
)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    service: ProductServiceDep,
    _admin: AdminUser,
) -> ProductRead:
    product = await service.update_product(
        product_id=product_id,
        name=payload.name,
        description=payload.description,
        price_cents=payload.price_cents,
        stock=payload.stock,
        category_id=payload.category_id,
        status=payload.status,
    )

    return ProductRead.model_validate(product)


@product_router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def archive_product(
    product_id: int,
    service: ProductServiceDep,
    _admin: AdminUser,
) -> None:
    await service.archive_product(product_id)
