# SimpleSDK

A lightweight async Python framework for building type-safe REST API clients, built on `aiohttp` and `pyserde`.

## Features

- Async HTTP client with automatic retry and exponential backoff
- Type-safe JSON serialization via `pyserde`
- Pluggable authentication (token-based auth included)
- Custom error models per API
- Configurable timeouts, headers, and user-agent

## Installation

Requires Python 3.12+.

```bash
pip install simple_sdk
```

## Quick Start

Define your models, API, and client:

```python
from serde import serde
from aiohttp import ClientSession
from simple_sdk import BaseApi, JsonApiClient, BaseConfiguration, TokenAuthenticator, CredentialLoader


# Models
@serde
class Profile:
    id: int
    name: str


# API
class MyApi(BaseApi):
    def __init__(self, session: ClientSession) -> None:
        super().__init__(session)

    async def get_profile(self) -> Profile:
        return await self.get("/profile", model=Profile)


# Client
class MyClient(JsonApiClient):
    def __init__(self, config: BaseConfiguration, auth: TokenAuthenticator) -> None:
        super().__init__(config, auth)
        self._my_api: MyApi | None = None

    @property
    def my_api(self) -> MyApi:
        if self._my_api is None:
            self._my_api = MyApi(self._session)
        return self._my_api
```

Then use it:

```python
import asyncio
from simple_sdk import BaseConfiguration


async def main():
    config = BaseConfiguration(base_url="http://localhost:8080")

    async with MyClient(config, auth=...) as client:
        profile = await client.my_api.get_profile()
        print(profile)


asyncio.run(main())
```

## License

This project is licensed under the [MIT License](LICENSE).
