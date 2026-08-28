from typing import Annotated

from fastapi import Depends

from app.core.database import DbSession
from app.modules.users.repositories.user_repository import UserRepository
from app.modules.users.services.user_service import UserService


def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]