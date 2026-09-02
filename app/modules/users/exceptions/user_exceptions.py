from app.core.exceptions import ForbiddenError, NotFoundError


class UserNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__("User not found")


class ForbiddenActionError(ForbiddenError):
    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(message)
