from abc import abstractmethod, ABC

from aiohttp import ClientSession


class Authenticator(ABC):
    @abstractmethod
    async def authenticate(self, session: ClientSession) -> ClientSession:
        """Authenticate and return an authenticated ClientSession."""
        pass


class CredentialLoader[TCreds](ABC):
    @abstractmethod
    async def load_credentials(self) -> TCreds:
        """Load credentials and return them."""
        pass


class TokenAuthenticator(Authenticator):
    """Example implementation of an Authenticator that uses a token to authenticate."""

    def __init__(self, token_loader: CredentialLoader[str]):
        self.token_loader = token_loader

    async def authenticate(self, session: ClientSession) -> ClientSession:
        """Authenticate using the provided token and return an authenticated session."""
        token = await self.token_loader.load_credentials()
        session.headers['Authorization'] = f"Bearer {token}"
        return session
