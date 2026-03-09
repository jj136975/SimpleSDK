from dataclasses import dataclass
from typing import override

from aiohttp import ClientSession

from simple_sdk.auth import Authenticator, CredentialLoader, TokenAuthenticator
from simple_sdk.client import JsonApiClient
from simple_sdk.config import BaseConfiguration

from .my_api import MyApi


@dataclass(kw_only=True)
class MyConfig(BaseConfiguration):
    any_additional_config: str = "default_value"


@dataclass
class MyAuthenticator(CredentialLoader):
    auth_url: str
    username: str
    password: str

    @override
    async def load_credentials(self) -> str:
        async with ClientSession() as session:
            async with session.post(
                    self.auth_url,
                    json={"username": self.username, "password": self.password}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                token = data.get("access_token")
                if not token:
                    raise ValueError("Authentication response did not contain an access token.")
                return token


class MyClient(JsonApiClient):
    def __init__(self, config: MyConfig, auth: MyAuthenticator) -> None:
        super().__init__(config, TokenAuthenticator(auth))
        self._my_api: MyApi | None = None

    @property
    def my_api(self) -> MyApi:
        if self._my_api is None:
            if self._session is None:
                raise RuntimeError(
                    "Client session not initialized. Use 'async with MyClient(...) as client' to initialize the session.")
            self._my_api = MyApi(self._session)
        return self._my_api
