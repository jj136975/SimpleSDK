from typing import override

import serde.json
from aiohttp import ClientSession

from .auth import Authenticator
from .config import BaseConfiguration


class ApiClient[TConfig: BaseConfiguration, TAuth: Authenticator]:
    """Base API client that handles authentication and session management."""

    def __init__(self, config: TConfig, auth: TAuth):
        self._config = config
        self._auth = auth
        self._session: ClientSession | None = None

    @property
    def config(self) -> TConfig:
        """Access the client's configuration."""
        return self._config

    @property
    def auth(self) -> TAuth:
        """Access the client's authentication loader."""
        return self._auth

    async def ensure_session(self) -> ClientSession:
        """Ensure that the client session is initialized and return it."""
        if self._session is None:
            session = self.config.create_session()
            self._session = await self.auth.authenticate(session)
        return self._session

    async def __aenter__(self):
        self._session = await self.ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None


class JsonApiClient[TConfig: BaseConfiguration, TAuth: Authenticator](ApiClient[TConfig, TAuth]):
    """API client that automatically sets Content-Type to application/json and uses serde for JSON serialization."""

    def __init__(self, config: TConfig, auth: TAuth) -> None:
        super().__init__(config, auth)
        self.config.headers['Content-Type'] = 'application/json'
        self.config.headers['Accept'] = 'application/json'

    @override
    async def ensure_session(self) -> ClientSession:
        """Ensure that the client session is initialized with JSON serialization and return it."""
        if self._session is None:
            session = self.config.create_session(
                json_serialize=lambda obj: serde.json.to_json(obj, skip_none=True)
            )
            self._session = await self.auth.authenticate(session)
        return self._session
