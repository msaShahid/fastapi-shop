from typing import Annotated

from fastapi import Depends

from app.core.database import DbSession
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.modules.auth.services.auth_service import AuthService


def get_auth_repository(
    db: DbSession,
) -> AuthRepository:
    return AuthRepository(db)


AuthRepositoryDep = Annotated[
    AuthRepository,
    Depends(get_auth_repository),
]


def get_auth_service(
    repository: AuthRepositoryDep,
) -> AuthService:
    return AuthService(repository)


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]
