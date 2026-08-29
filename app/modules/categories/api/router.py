from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.dependencies.auth import AdminUser
from app.modules.categories.dependencies.category_deps import CategoryServiceDep
from app.modules.categories.exceptions.category_exceptions import (
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
)
from app.modules.categories.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.shared.pagination.schemas import PageParams, PaginatedResponse

category_router = APIRouter(prefix="/categories", tags=["categories"])


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


@category_router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate, service: CategoryServiceDep, _admin: AdminUser
) -> CategoryRead:

    try:
        category = await service.create_category(
            name=payload.name, description=payload.description
        )
    except CategoryNameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists",
        ) from exc

    return CategoryRead.model_validate(category)


@category_router.get("", response_model=PaginatedResponse[CategoryRead])
async def list_categories(
    service: CategoryServiceDep, params: PageParams = Depends()
) -> PaginatedResponse[CategoryRead]:

    categories, total = await service.list_categories(offset=params.offset, limit=params.page_size)
    return PaginatedResponse(
        items=[CategoryRead.model_validate(c) for c in categories],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@category_router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, service: CategoryServiceDep) -> CategoryRead:
    try:
        category = await service.get_category(category_id)
    except CategoryNotFoundError as exc:
        raise _not_found() from exc
    return CategoryRead.model_validate(category)


@category_router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    service: CategoryServiceDep,
    _admin: AdminUser,
) -> CategoryRead:
    try:
        category = await service.update_category(
            category_id=category_id,
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
        )
    except CategoryNotFoundError as exc:
        raise _not_found() from exc
    except CategoryNameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists",
        ) from exc

    return CategoryRead.model_validate(category)


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_category(
    category_id: int, service: CategoryServiceDep, _admin: AdminUser
) -> None:
    try:
        await service.deactivate_category(category_id)
    except CategoryNotFoundError as exc:
        raise _not_found() from exc
