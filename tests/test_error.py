class AppError(Exception):
    def __init__(self, message="An error occurred"):
        self.message = message
        super().__init__(message)


class ConflictError(AppError):
    def __init__(self, message="Resource already exists"):
        super().__init__(message)


class EmailAlreadyExistsError(ConflictError):
    pass


def test_email_already_exists_is_conflict_error():
    exc = EmailAlreadyExistsError(
        "shahid@example.com already registered"
    )

    assert isinstance(exc, ConflictError)


def test_email_already_exists_message():
    exc = EmailAlreadyExistsError(
        "shahid@example.com already registered"
    )

    assert exc.message == "shahid@example.com already registered"
