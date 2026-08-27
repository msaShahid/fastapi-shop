import uuid

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import create_access_token, create_refresh_token
from app.modules.auth.dependencies.auth import get_current_user, require_admin
from app.shared.enums.roles import UserRole


def _bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


async def test_valid_access_token_returns_user(fake_repository, make_user):
    user = make_user()
    fake_repository.users_by_id[user.id] = user
    token = create_access_token(subject=str(user.id))

    result = await get_current_user(_bearer(token), fake_repository)

    assert result.id == user.id


async def test_refresh_token_rejected_as_access_token(fake_repository, make_user):
    user = make_user()
    fake_repository.users_by_id[user.id] = user
    refresh_token = create_refresh_token(subject=str(user.id))

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(_bearer(refresh_token), fake_repository)
    assert exc_info.value.status_code == 401


async def test_inactive_user_rejected(fake_repository, make_user):
    user = make_user(is_active=False)
    fake_repository.users_by_id[user.id] = user
    token = create_access_token(subject=str(user.id))

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(_bearer(token), fake_repository)
    assert exc_info.value.status_code == 401


async def test_garbage_token_rejected(fake_repository):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(_bearer("not-a-real-token"), fake_repository)
    assert exc_info.value.status_code == 401


async def test_token_for_nonexistent_user_rejected(fake_repository):
    ghost_token = create_access_token(subject=str(uuid.uuid4()))

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(_bearer(ghost_token), fake_repository)
    assert exc_info.value.status_code == 401


async def test_require_admin_rejects_regular_user(make_user):
    user = make_user(role=UserRole.USER)

    with pytest.raises(HTTPException) as exc_info:
        await require_admin(user)
    assert exc_info.value.status_code == 403


async def test_require_admin_accepts_admin_user(make_user):
    admin = make_user(role=UserRole.ADMIN)

    result = await require_admin(admin)

    assert result.id == admin.id