from dataclasses import dataclass
from datetime import UTC, datetime

from alcc.shared.domain.base import AggregateRoot
from alcc.shared.domain.enums import UserRole
from alcc.shared.domain.exceptions import ValidationError


@dataclass
class User(AggregateRoot):
    email: str = ""
    hashed_password: str = ""
    full_name: str = ""
    role: UserRole = UserRole.OPERATOR
    is_active: bool = True

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def change_role(self, role: UserRole) -> None:
        self.role = role
        self.updated_at = datetime.now(UTC)

    def can_dispatch(self) -> bool:
        return self.role in (UserRole.DISPATCHER, UserRole.ADMIN)

    def can_operate_fleet(self) -> bool:
        return self.role in (UserRole.OPERATOR, UserRole.ADMIN)

    def can_view_analytics(self) -> bool:
        return self.role in (UserRole.ANALYST, UserRole.ADMIN, UserRole.OPERATOR)

    @staticmethod
    def validate_email(email: str) -> None:
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValidationError("Invalid email address")
