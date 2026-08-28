import uuid

from app.modules.auth.models.user import User
from app.modules.users.exceptions.user_exceptions import (
    ForbiddenActionError,
    UserNotFoundError,
)
from app.modules.users.repositories.user_repository import UserRepository
from app.shared.enums.roles import UserRole


class UserService:

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def get_user(self, *, target_user_id: uuid.UUID, current_user: User) -> User:
       
        if current_user.role != UserRole.ADMIN and current_user.id != target_user_id:
            raise ForbiddenActionError("You can only view your own profile")

        user = await self.repository.get_by_id(target_user_id)
        if user is None:
            raise UserNotFoundError(target_user_id)
        return user

    async def list_users(
        self, *, current_user: User, offset: int, limit: int
    ) -> tuple[list[User], int]:

        if current_user.role != UserRole.ADMIN:
            raise ForbiddenActionError("Only administrators can list all users")

        return await self.repository.list_paginated(offset=offset, limit=limit)

    async def update_user(
        self,
        *,
        target_user_id: uuid.UUID,
        current_user: User,
        username: str | None,
        email: str | None,
        role: UserRole | None,
    ) -> User:
        if current_user.role != UserRole.ADMIN and current_user.id != target_user_id:
            raise ForbiddenActionError("You can only update your own profile")

        if role is not None and current_user.role != UserRole.ADMIN:
            raise ForbiddenActionError("Only administrators can change roles")

        user = await self.repository.get_by_id(target_user_id)
        if user is None:
            raise UserNotFoundError(target_user_id)

        updates = {}
        if username is not None:
            updates["username"] = username
        if email is not None:
            updates["email"] = email
        if role is not None:
            updates["role"] = role

        return await self.repository.update(user, **updates)

    async def deactivate_user(
        self, *, target_user_id: uuid.UUID, current_user: User
    ) -> User:

        if current_user.role != UserRole.ADMIN and current_user.id != target_user_id:
            raise ForbiddenActionError("You can only deactivate your own account")

        user = await self.repository.get_by_id(target_user_id)
        if user is None:
            raise UserNotFoundError(target_user_id)

        return await self.repository.deactivate(user)
