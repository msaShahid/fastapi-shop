import uuid

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies.auth import CurrentUser
from app.modules.auth.schemas.auth import UserRead
from app.modules.users.dependencies.user_deps import UserServiceDep
from app.modules.users.schemas.user import UserUpdate
from app.shared.pagination.schemas import PageParams, PaginatedResponse

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@users_router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    current_user: CurrentUser,
    service: UserServiceDep,
    params: PageParams = Depends(),
) -> PaginatedResponse[UserRead]:
    users, total = await service.list_users(
        current_user=current_user,
        offset=params.offset,
        limit=params.page_size,
    )

    return PaginatedResponse(
        items=[UserRead.model_validate(u) for u in users],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@users_router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    service: UserServiceDep,
) -> UserRead:
    user = await service.get_user(
        target_user_id=user_id,
        current_user=current_user,
    )

    return UserRead.model_validate(user)


@users_router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: CurrentUser,
    service: UserServiceDep,
) -> UserRead:
    user = await service.update_user(
        target_user_id=user_id,
        current_user=current_user,
        username=payload.username,
        email=payload.email,
        role=payload.role,
    )

    return UserRead.model_validate(user)


@users_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    service: UserServiceDep,
) -> None:
    await service.deactivate_user(
        target_user_id=user_id,
        current_user=current_user,
    )
