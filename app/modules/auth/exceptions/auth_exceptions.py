class EmailAlreadyExistsError(Exception):
    pass


class UsernameAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass

class InvalidRefreshTokenError(Exception):
    pass

class revoke_refresh_token(Exception):
    pass