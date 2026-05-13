from app.core.security import hash_password, verify_password


def test_hash_and_verify_password():
    password = "secret123"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2b$")
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False