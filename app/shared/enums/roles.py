import enum


class UserRole(str, enum.StrEnum):

    USER = "user"
    ADMIN = "admin"