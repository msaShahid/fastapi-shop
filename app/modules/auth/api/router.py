from fastapi import APIRouter, HTTPException, status

from app.modules.auth.dependencies.auth import AuthServiceDep, CurrentUser
from app.modules.auth.exceptions.auth_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UsernameAlreadyExistsError,
)
from app.modules.auth.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserRead,
)

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


@auth_router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUser) -> UserRead:

    return UserRead.model_validate(current_user)

@auth_router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, service: AuthServiceDep) -> TokenPair:

    try:
        return await service.refresh(refresh_token=payload.refresh_token)
    except InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, service: AuthServiceDep) -> None:

    await service.logout(refresh_token=payload.refresh_token)
