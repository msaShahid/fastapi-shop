from pydantic import BaseModel, EmailStr, Field

from app.shared.enums.roles import UserRole


class UserUpdate(BaseModel):

    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    role: UserRole | None = None