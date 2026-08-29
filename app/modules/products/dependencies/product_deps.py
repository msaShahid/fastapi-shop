from typing import Annotated

from fastapi import Depends

from app.core.database import DbSession
from app.modules.categories.dependencies.category_deps import get_category_repository
from app.modules.categories.repositories.category_repository import CategoryRepository
from app.modules.products.repositories.product_repository import ProductRepository
from app.modules.products.services.product_service import ProductService


def get_product_repository(db: DbSession) -> ProductRepository:
    return ProductRepository(db)


def get_product_service(
    repository: Annotated[ProductRepository, Depends(get_product_repository)],
    category_repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> ProductService:

    return ProductService(repository, category_repository)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
