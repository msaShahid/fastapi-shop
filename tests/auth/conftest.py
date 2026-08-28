import uuid
from dataclasses import dataclass
from datetime import datetime

import pytest

from app.modules.auth.models.user import User
from app.shared.enums.roles import UserRole


@dataclass
class FakeRefreshToken:
    """
    Mirrors the real RefreshToken model's shape closely enough for
    AuthService's logic to operate on identically -- it reads
    .revoked, .expires_at, .user_id, exactly like the real ORM object.
    """

    jti: str
    user_id: uuid.UUID
    expires_at: datetime
    revoked: bool = False


class FakeAuthRepository:
    """
    Implements the same interface as AuthRepository, backed by plain
    dicts instead of Postgres. This is the direct payoff of the
    repository/service split from our architecture: AuthService never
    imports SQLAlchemy, so it can be tested against this fake with zero
    database connection, running in milliseconds.
    """

    def __init__(self) -> None:
        self.users_by_id: dict[uuid.UUID, User] = {}
        self.users_by_email: dict[str, User] = {}
        self.users_by_username: dict[str, User] = {}
        self.refresh_tokens: dict[str, FakeRefreshToken] = {}

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.users_by_id.get(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return self.users_by_email.get(email)

    async def get_user_by_username(self, username: str) -> User | None:
        return self.users_by_username.get(username)

    async def create_user(self, *, username: str, email: str, password_hash: str) -> User:
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            password_hash=password_hash,
            role=UserRole.USER,
            is_active=True,
        )
        self.users_by_id[user.id] = user
        self.users_by_email[email] = user
        self.users_by_username[username] = user
        return user

    async def store_refresh_token(
        self, *, user_id: uuid.UUID, jti: str, expires_at: datetime
    ) -> FakeRefreshToken:
        token = FakeRefreshToken(jti=jti, user_id=user_id, expires_at=expires_at)
        self.refresh_tokens[jti] = token
        return token

    async def get_refresh_token_by_jti(self, jti: str) -> FakeRefreshToken | None:
        return self.refresh_tokens.get(jti)

    async def revoke_refresh_token(self, token: FakeRefreshToken) -> None:
        token.revoked = True


@pytest.fixture
def fake_repository() -> FakeAuthRepository:
    """A fresh, empty fake repository for each test -- no shared state leaks between tests."""
    return FakeAuthRepository()


@pytest.fixture
def make_user():
    """
    Factory fixture: call make_user() inside a test to get a User object
    with sensible defaults, overridable via kwargs -- e.g.
    make_user(role=UserRole.ADMIN, is_active=False).
    """

    def _make_user(**overrides) -> User:
        defaults = dict(
            id=uuid.uuid4(),
            username="testuser",
            email="testuser@example.com",
            password_hash="irrelevant-for-these-tests",
            role=UserRole.USER,
            is_active=True,
        )
        defaults.update(overrides)
        return User(**defaults)

    return _make_user