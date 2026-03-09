from basic_sdk.client import MyConfig
from examples.basic_api.basic_sdk.client import MyClient, MyAuthenticator


async def main() -> None:
    config = MyConfig(
        base_url="http://localhost:8080",
        agent="My Python SDK",
    )

    MyAuthenticator(
        auth_url="http://localhost:8080/auth",
        username="MyUser",
        password="MySecurePassword123!",
    )

    async with MyClient(config) as client:


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
