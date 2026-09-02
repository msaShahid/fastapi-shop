from app.core.exceptions import ConflictError, UnauthorizedError


class EmailAlreadyExistsError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__("An account with this email already exists")


class UsernameAlreadyExistsError(ConflictError):
    def __init__(self, username: str) -> None:
        super().__init__("This username is already taken")


class InvalidCredentialsError(UnauthorizedError):
    """
    Deliberately the SAME exception for both 'no such email' and 'wrong
    password'. If these were distinguishable to a caller, an attacker
    could enumerate valid registered emails by checking which error a
    login attempt returns -- a real, well-known information leak.
    """

    def __init__(self) -> None:
        super().__init__("Incorrect email or password")


class InvalidRefreshTokenError(UnauthorizedError):
    """
    Covers: malformed token, wrong token type, unknown jti, expired, or
    already-revoked (rotation reuse). All map to the same 401 -- there's
    no legitimate reason a client needs to distinguish these.
    """

    def __init__(self) -> None:
        super().__init__("Invalid or expired refresh token")