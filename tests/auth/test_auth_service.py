import pytest

from app.core.security import decode_token
from app.modules.auth.exceptions.auth_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UsernameAlreadyExistsError,
)
from app.modules.auth.services.auth_service import AuthService


@pytest.fixture
def auth_service(fake_repository) -> AuthService:
    return AuthService(fake_repository)


async def test_register_creates_user_with_hashed_password(auth_service):
    user = await auth_service.register(
        username="shahid", email="shahid@example.com", password="supersecret123"
    )
    assert user.username == "shahid"
    assert user.email == "shahid@example.com"
    # The core guarantee: whatever got stored is NOT the plain password.
    assert user.password_hash != "supersecret123"


async def test_register_rejects_duplicate_email(auth_service):
    await auth_service.register(username="first", email="dup@example.com", password="password123")
    with pytest.raises(EmailAlreadyExistsError):
        await auth_service.register(
            username="second", email="dup@example.com", password="password123"
        )


async def test_register_rejects_duplicate_username(auth_service):
    await auth_service.register(username="dupuser", email="a@example.com", password="password123")
    with pytest.raises(UsernameAlreadyExistsError):
        await auth_service.register(
            username="dupuser", email="b@example.com", password="password123"
        )


async def test_login_succeeds_with_correct_credentials(auth_service):
    user = await auth_service.register(
        username="shahid", email="shahid@example.com", password="supersecret123"
    )
    tokens = await auth_service.login(email="shahid@example.com", password="supersecret123")

    payload = decode_token(tokens.access_token)
    assert payload["sub"] == str(user.id)
    assert payload["type"] == "access"


async def test_login_persists_refresh_token(auth_service, fake_repository):
    await auth_service.register(
        username="shahid", email="shahid@example.com", password="supersecret123"
    )
    await auth_service.login(email="shahid@example.com", password="supersecret123")

    assert len(fake_repository.refresh_tokens) == 1


async def test_login_rejects_wrong_password(auth_service):
    await auth_service.register(
        username="shahid", email="shahid@example.com", password="correct-password"
    )
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(email="shahid@example.com", password="wrong-password")


async def test_login_rejects_nonexistent_email_with_same_error_as_wrong_password(auth_service):
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(email="nobody@example.com", password="whatever123")
