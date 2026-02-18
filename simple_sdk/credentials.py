from abc import ABC, abstractmethod
from typing import override


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class CredentialLoader[TConfig = None, TAuth = str](ABC):
    @abstractmethod
    async def authenticate(self, config: TConfig) -> TAuth:
        """Authenticate and return credentials of type T."""
        pass

    def get_auth_header_prefix(self) -> str | None:
        """Return the prefix to use in the Authorization header, or None for no prefix."""
        return "Bearer"


class StaticCredentialLoader(CredentialLoader):
    def __init__(self, token: str):
        self.token = token

    @override
    async def authenticate(self, _) -> str:
        return self.token
