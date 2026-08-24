from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "TestPassword123!"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_access_token():
    subject = "test-user-id"

    token = create_access_token(subject)
    payload = decode_token(token)

    assert token
    assert payload["sub"] == subject
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload


def test_refresh_token():
    subject = "test-user-id"

    token = create_refresh_token(subject)
    payload = decode_token(token)

    assert token
    assert payload["sub"] == subject
    assert payload["type"] == "refresh"
    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload


def test_access_and_refresh_tokens_are_different():
    subject = "test-user-id"

    access_token = create_access_token(subject)
    refresh_token = create_refresh_token(subject)

    assert access_token != refresh_token

# docker compose exec api pytest tests/test_security.py -v