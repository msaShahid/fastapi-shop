from fastapi import APIRouter, HTTPException, status

from app.modules.auth.dependencies.auth import AuthServiceDep
from app.modules.auth.exceptions.auth_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UsernameAlreadyExistsError,
)
from app.modules.auth.schemas.auth import LoginRequest, RegisterRequest, TokenPair, UserRead

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, service: AuthServiceDep) -> UserRead:

    try:
        user = await service.register(
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
    except EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc
    except UsernameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken",
        ) from exc

    return UserRead.model_validate(user)


@auth_router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, service: AuthServiceDep) -> TokenPair:
    try:
        return await service.login(email=payload.email, password=payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        ) from exc
