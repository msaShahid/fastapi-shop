from datetime import UTC, datetime

from jose import jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.modules.auth.exceptions.auth_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UsernameAlreadyExistsError,
)
from app.modules.auth.models.user import User
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.modules.auth.schemas.auth import TokenPair


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    async def register(self, *, username: str, email: str, password: str) -> User:

        if await self.repository.get_user_by_email(email) is not None:
            raise EmailAlreadyExistsError(email)

        if await self.repository.get_user_by_username(username) is not None:
            raise UsernameAlreadyExistsError(username)

        password_hash = hash_password(password)
        return await self.repository.create_user(
            username=username,
            email=email,
            password_hash=password_hash,
        )

    async def login(self, *, email: str, password: str) -> TokenPair:

        user = await self.repository.get_user_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        refresh_payload = jwt.get_unverified_claims(refresh_token)
        expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=UTC)

        await self.repository.store_refresh_token(
            user_id=user.id,
            jti=refresh_payload["jti"],
            expires_at=expires_at,
        )

        return TokenPair(access_token=access_token, refresh_token=refresh_token)
