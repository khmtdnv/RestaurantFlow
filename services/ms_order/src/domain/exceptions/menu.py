from domain.exceptions.base import DomainError


class MenuItemNotFoundError(DomainError):
    pass


class MenuItemUnavailableError(DomainError):
    pass
