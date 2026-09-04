from typing import Annotated

from fastapi import Depends

from app.core.database import DbSession
from app.core.storage.interface import StorageService
from app.core.storage.local import LocalStorageService
from app.modules.categories.repositories.category_repository import (
    CategoryRepository,
)
from app.modules.categories.services.category_service import CategoryService


def get_category_repository(
    db: DbSession,
) -> CategoryRepository:
    return CategoryRepository(db)


def get_storage_service() -> StorageService:
    return LocalStorageService(
        root_path="media",
        base_url="/media",
    )


StorageServiceDep = Annotated[
    StorageService,
    Depends(get_storage_service),
]


def get_category_service(
    repository: Annotated[
        CategoryRepository,
        Depends(get_category_repository),
    ],
    storage: StorageServiceDep,
) -> CategoryService:
    return CategoryService(
        repository=repository,
        storage=storage,
    )


CategoryServiceDep = Annotated[
    CategoryService,
    Depends(get_category_service),
]
