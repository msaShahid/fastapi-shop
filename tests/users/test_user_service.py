import uuid

import pytest

from app.modules.users.exceptions.user_exceptions import ForbiddenActionError, UserNotFoundError
from app.modules.users.services.user_service import UserService
from app.shared.enums.roles import UserRole


@pytest.fixture
def user_service(fake_user_repository) -> UserService:
    return UserService(fake_user_repository)


# --- get_user ---


async def test_user_can_view_own_profile(user_service, fake_user_repository, make_user):
    user = make_user()
    fake_user_repository.users[user.id] = user

    result = await user_service.get_user(target_user_id=user.id, current_user=user)

    assert result.id == user.id


async def test_user_cannot_view_someone_elses_profile(user_service, fake_user_repository, make_user):
    owner = make_user()
    other = make_user()
    fake_user_repository.users[owner.id] = owner

    with pytest.raises(ForbiddenActionError):
        await user_service.get_user(target_user_id=owner.id, current_user=other)


async def test_admin_can_view_anyones_profile(user_service, fake_user_repository, make_user):
    admin = make_user(role=UserRole.ADMIN)
    other = make_user()
    fake_user_repository.users[other.id] = other

    result = await user_service.get_user(target_user_id=other.id, current_user=admin)

    assert result.id == other.id


async def test_get_nonexistent_user_raises_not_found(user_service, make_user):
    admin = make_user(role=UserRole.ADMIN)

    with pytest.raises(UserNotFoundError):
        await user_service.get_user(target_user_id=uuid.uuid4(), current_user=admin)


# --- list_users ---


async def test_regular_user_cannot_list_all_users(user_service, make_user):
    user = make_user()

    with pytest.raises(ForbiddenActionError):
        await user_service.list_users(current_user=user, offset=0, limit=20)


async def test_admin_can_list_all_users(user_service, fake_user_repository, make_user):
    admin = make_user(role=UserRole.ADMIN)
    for _ in range(3):
        u = make_user()
        fake_user_repository.users[u.id] = u

    users, total = await user_service.list_users(current_user=admin, offset=0, limit=20)

    assert total == 3
    assert len(users) == 3


# --- update_user ---


async def test_user_can_update_own_username(user_service, fake_user_repository, make_user):
    user = make_user()
    fake_user_repository.users[user.id] = user

    updated = await user_service.update_user(
        target_user_id=user.id,
        current_user=user,
        username="newname",
        email=None,
        role=None,
    )

    assert updated.username == "newname"


async def test_user_cannot_update_someone_elses_profile(user_service, fake_user_repository, make_user):
    owner = make_user()
    other = make_user()
    fake_user_repository.users[owner.id] = owner

    with pytest.raises(ForbiddenActionError):
        await user_service.update_user(
            target_user_id=owner.id,
            current_user=other,
            username="hacked",
            email=None,
            role=None,
        )


async def test_user_cannot_promote_themselves_to_admin(user_service, fake_user_repository, make_user):
    """
    The privilege-escalation guard, tested directly: a regular user
    editing their OWN profile (which is otherwise allowed) must still be
    blocked from setting role=ADMIN.
    """
    user = make_user(role=UserRole.USER)
    fake_user_repository.users[user.id] = user

    with pytest.raises(ForbiddenActionError):
        await user_service.update_user(
            target_user_id=user.id,
            current_user=user,
            username=None,
            email=None,
            role=UserRole.ADMIN,
        )


async def test_admin_can_change_another_users_role(user_service, fake_user_repository, make_user):
    admin = make_user(role=UserRole.ADMIN)
    target = make_user(role=UserRole.USER)
    fake_user_repository.users[target.id] = target

    updated = await user_service.update_user(
        target_user_id=target.id,
        current_user=admin,
        username=None,
        email=None,
        role=UserRole.ADMIN,
    )

    assert updated.role == UserRole.ADMIN


# --- deactivate_user ---


async def test_user_can_deactivate_own_account(user_service, fake_user_repository, make_user):
    user = make_user()
    fake_user_repository.users[user.id] = user

    result = await user_service.deactivate_user(target_user_id=user.id, current_user=user)

    assert result.is_active is False


async def test_user_cannot_deactivate_someone_elses_account(
    user_service, fake_user_repository, make_user
):
    owner = make_user()
    other = make_user()
    fake_user_repository.users[owner.id] = owner

    with pytest.raises(ForbiddenActionError):
        await user_service.deactivate_user(target_user_id=owner.id, current_user=other)


async def test_admin_can_deactivate_any_account(user_service, fake_user_repository, make_user):
    admin = make_user(role=UserRole.ADMIN)
    target = make_user()
    fake_user_repository.users[target.id] = target

    result = await user_service.deactivate_user(target_user_id=target.id, current_user=admin)

    assert result.is_active is False