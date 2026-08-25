import uuid

import pytest

from app.core.security import decode_token, hash_password
from app.modules.auth.exceptions.auth_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UsernameAlreadyExistsError,
)
from app.modules.auth.models.user import User
from app.modules.auth.services.auth_service import AuthService


class FakeRepository:
    """
    In-memory fake repository implementing the same interface as
    AuthRepository.

    This allows AuthService to be tested without PostgreSQL.
    """

    def __init__(self):
        self.users_by_email = {}
        self.users_by_username = {}
        self.refresh_tokens = {}

    async def get_user_by_email(self, email):
        return self.users_by_email.get(email)

    async def get_user_by_username(self, username):
        return self.users_by_username.get(username)

    async def create_user(self, *, username, email, password_hash):
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            password_hash=password_hash,
        )

        self.users_by_email[email] = user
        self.users_by_username[username] = user

        return user

    async def store_refresh_token(self, *, user_id, jti, expires_at):
        self.refresh_tokens[jti] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "revoked": False,
        }


@pytest.fixture
def repository():
    return FakeRepository()


@pytest.fixture
def service(repository):
    return AuthService(repository)


@pytest.mark.asyncio
async def test_register_success(service):
    user = await service.register(
        username="shahid",
        email="shahid@example.com",
        password="supersecret123",
    )

    assert user.username == "shahid"
    assert user.email == "shahid@example.com"

    # Password must never be stored as plain text.
    assert user.password_hash != "supersecret123"

    # Verify that the stored password hash actually works.
    from app.core.security import verify_password

    assert verify_password("supersecret123", user.password_hash)


@pytest.mark.asyncio
async def test_duplicate_email_rejected(service):
    await service.register(
        username="shahid",
        email="shahid@example.com",
        password="supersecret123",
    )

    with pytest.raises(EmailAlreadyExistsError):
        await service.register(
            username="different",
            email="shahid@example.com",
            password="whatever123",
        )


@pytest.mark.asyncio
async def test_duplicate_username_rejected(service):
    await service.register(
        username="shahid",
        email="shahid@example.com",
        password="supersecret123",
    )

    with pytest.raises(UsernameAlreadyExistsError):
        await service.register(
            username="shahid",
            email="different@example.com",
            password="whatever123",
        )


@pytest.mark.asyncio
async def test_login_success(service, repository):
    user = await service.register(
        username="shahid",
        email="shahid@example.com",
        password="supersecret123",
    )

    tokens = await service.login(
        email="shahid@example.com",
        password="supersecret123",
    )

    assert tokens.access_token
    assert tokens.refresh_token

    payload = decode_token(tokens.access_token)

    assert payload["sub"] == str(user.id)

    # Refresh token should be persisted.
    assert len(repository.refresh_tokens) == 1


@pytest.mark.asyncio
async def test_wrong_password_rejected(service):
    await service.register(
        username="shahid",
        email="shahid@example.com",
        password="supersecret123",
    )

    with pytest.raises(InvalidCredentialsError):
        await service.login(
            email="shahid@example.com",
            password="wrong-password",
        )


@pytest.mark.asyncio
async def test_nonexistent_email_rejected_with_same_error(service):
    with pytest.raises(InvalidCredentialsError):
        await service.login(
            email="nobody@example.com",
            password="whatever",
        )


@pytest.mark.asyncio
async def test_wrong_password_and_nonexistent_email_use_same_exception(
    service,
):
    await service.register(
        username="shahid",
        email="shahid@example.com",
        password="supersecret123",
    )

    with pytest.raises(InvalidCredentialsError) as wrong_password:
        await service.login(
            email="shahid@example.com",
            password="wrong-password",
        )

    with pytest.raises(InvalidCredentialsError) as nonexistent_email:
        await service.login(
            email="nobody@example.com",
            password="whatever",
        )

    assert type(wrong_password.value) is type(nonexistent_email.value)


@pytest.mark.asyncio
async def test_service_layer_uses_no_database(service, repository):
    user = await service.register(
        username="shahid",
        email="shahid@example.com",
        password="supersecret123",
    )

    assert user.id is not None
    assert len(repository.users_by_email) == 1
    assert len(repository.users_by_username) == 1
