class DomainException(Exception):
    """Base domain exception."""


class NotFoundError(DomainException):
    pass


class ValidationError(DomainException):
    pass


class ConflictError(DomainException):
    pass


class AuthorizationError(DomainException):
    pass
