from app.core.exceptions import ConflictError, InvalidStateError, NotFoundError


class ProductNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__("Product not found")


class SkuAlreadyExistsError(ConflictError):
    def __init__(self) -> None:
        super().__init__("A product with this SKU already exists")


class InvalidCategoryError(InvalidStateError):
    def __init__(self) -> None:
        super().__init__(
            "category_id does not refer to an existing, active category"
        )
