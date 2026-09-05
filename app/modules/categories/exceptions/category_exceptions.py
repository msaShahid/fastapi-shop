from app.core.exceptions import ConflictError, NotFoundError


class CategoryNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__("Category not found")


class CategoryNameAlreadyExistsError(ConflictError):
    def __init__(self) -> None:
        super().__init__("A category with this name already exists")
