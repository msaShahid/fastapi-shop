from typing import Annotated

from fastapi import Depends

from app.core.database import DbSession
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.categories.services.category_service import CategoryService


def get_category_repository(db: DbSession) -> CategoryRepository:
    return CategoryRepository(db)


def get_category_service(
    repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> CategoryService:
    return CategoryService(repository)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
