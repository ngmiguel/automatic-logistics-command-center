from datetime import timedelta
from uuid import uuid4

from alcc.auth.infrastructure.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from alcc.shared.domain.enums import UserRole


class TestSecurity:
    def test_hash_and_verify_password(self):
        hashed = hash_password("securepassword123")
        assert hashed != "securepassword123"
        assert verify_password("securepassword123", hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_create_and_decode_token(self):
        user_id = uuid4()
        token = create_access_token(user_id, "test@alcc.io", UserRole.OPERATOR)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["email"] == "test@alcc.io"
        assert payload["role"] == "operator"

    def test_decode_invalid_token(self):
        assert decode_access_token("invalid.token.here") is None

    def test_token_with_custom_expiry(self):
        user_id = uuid4()
        token = create_access_token(
            user_id, "test@alcc.io", UserRole.ADMIN, expires_delta=timedelta(hours=1)
        )
        payload = decode_access_token(token)
        assert payload["role"] == "admin"

    def test_different_roles_in_token(self):
        for role in UserRole:
            token = create_access_token(uuid4(), "r@test.io", role)
            payload = decode_access_token(token)
            assert payload["role"] == role.value
