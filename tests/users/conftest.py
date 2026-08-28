import uuid

import pytest

from app.modules.auth.models.user import User
from app.shared.enums.roles import UserRole


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.users.get(user_id)

    async def list_paginated(self, *, offset: int, limit: int) -> tuple[list[User], int]:
        all_users = sorted(self.users.values(), key=lambda u: u.username)
        total = len(all_users)
        return all_users[offset : offset + limit], total

    async def update(self, user: User, **fields) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        return user

    async def deactivate(self, user: User) -> User:
        user.is_active = False
        return user


@pytest.fixture
def fake_user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def make_user():
    def _make_user(**overrides) -> User:
        defaults = dict(
            id=uuid.uuid4(),
            username="shahid",
            email="shahid@example.com",
            password_hash="irrelevant",
            role=UserRole.USER,
            is_active=True,
        )
        defaults.update(overrides)
        return User(**defaults)

    return _make_user