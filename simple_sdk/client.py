from typing import override

import serde.json
from aiohttp import ClientSession

from .config import BaseConfiguration
from .credentials import CredentialLoader


class ApiClient[TConfig: BaseConfiguration, TAuth = str]:
    """Base API client that handles authentication and session management."""
    def __init__(self, config: TConfig, auth: CredentialLoader[TConfig, TAuth]):
        self._config = config
        self._auth = auth
        self._session: ClientSession | None = None

    @property
    def config(self) -> TConfig:
        """Access the client's configuration."""
        return self._config

    @property
    def auth(self) -> CredentialLoader[TConfig, TAuth]:
        """Access the client's authentication loader."""
        return self._auth

    def _create_headers(self, api_key: TAuth, ) -> dict[str, str]:
        """Create headers for the API session, including authentication and user agent."""
        headers = self._config.headers.copy()

        if auth_prefix := self._auth.get_auth_header_prefix():
            headers['Authorization'] = auth_prefix + " " + api_key
        else:
            headers['Authorization'] = api_key

        if self._config.agent:
            headers['User-Agent'] = self._config.agent

        return headers

    async def _create_session(self) -> ClientSession:
        """Create an aiohttp ClientSession with the appropriate headers for authentication."""
        api_key = await self._auth.authenticate(self._config)
        headers = self._create_headers(api_key)

        return ClientSession(
            base_url=self._config.base_url,
            headers=headers,
        )

    async def __aenter__(self):
        self._session = await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None


class JsonApiClient[TConfig: BaseConfiguration, TAuth = str](ApiClient[TConfig, TAuth]):
    """API client that automatically sets Content-Type to application/json and uses serde for JSON serialization."""
    @override
    def _create_headers(self, api_key: TAuth) -> dict[str, str]:
        """Extend the base headers to include Content-Type for JSON requests."""
        headers = super()._create_headers(api_key)
        headers['Content-Type'] = 'application/json'
        return headers

    @override
    async def _create_session(self) -> ClientSession | None:
        """Create an aiohttp ClientSession with JSON serialization using serde."""
        api_key = await self._auth.authenticate(self._config)
        headers = self._create_headers(api_key)

        return ClientSession(
            base_url=self._config.base_url,
            headers=headers,
            json_serialize=lambda obj: serde.json.to_json(obj, skip_none=True),
        )
