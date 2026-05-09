from app.core.jwt import create_access_token, create_refresh_token, decode_token


def test_create_and_decode_access_token():
    token = create_access_token({"sub": "user-123"})
    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_and_decode_refresh_token():
    token = create_refresh_token({"sub": "user-456"})
    payload = decode_token(token)

    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"