from uuid import uuid4

import pytest

from alcc.auth.domain.entities import User
from alcc.shared.domain.enums import UserRole
from alcc.shared.domain.exceptions import ValidationError


class TestUserDomain:
    def test_default_role_is_operator(self):
        user = User(email="test@alcc.io")
        assert user.role == UserRole.OPERATOR
        assert user.is_active is True

    def test_deactivate_user(self):
        user = User(email="test@alcc.io")
        user.deactivate()
        assert user.is_active is False

    def test_change_role(self):
        user = User(email="test@alcc.io")
        user.change_role(UserRole.ADMIN)
        assert user.role == UserRole.ADMIN

    def test_can_dispatch(self):
        assert User(role=UserRole.DISPATCHER).can_dispatch()
        assert User(role=UserRole.ADMIN).can_dispatch()
        assert not User(role=UserRole.OPERATOR).can_dispatch()

    def test_can_operate_fleet(self):
        assert User(role=UserRole.OPERATOR).can_operate_fleet()
        assert User(role=UserRole.ADMIN).can_operate_fleet()
        assert not User(role=UserRole.ANALYST).can_operate_fleet()

    def test_can_view_analytics(self):
        assert User(role=UserRole.ANALYST).can_view_analytics()
        assert User(role=UserRole.OPERATOR).can_view_analytics()
        assert not User(role=UserRole.DISPATCHER).can_view_analytics()

    def test_validate_email_valid(self):
        User.validate_email("valid@alcc.io")

    def test_validate_email_invalid(self):
        with pytest.raises(ValidationError):
            User.validate_email("invalid-email")

    def test_user_is_aggregate_root(self):
        user = User(email="test@alcc.io", full_name="Test")
        assert user.id is not None
