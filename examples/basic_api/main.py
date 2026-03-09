from basic_sdk.client import MyConfig, MyClient, MyAuthenticator


async def main() -> None:
    config = MyConfig(
        base_url="http://localhost:8080",
        agent="My Python SDK",
    )

    auth = MyAuthenticator(
        auth_url="http://localhost:8080/auth",
        username="MyUser",
        password="MySecurePassword123!",
    )

    async with MyClient(config, auth) as client:
        profile = await client.my_api.get_my_profile()
        print(profile)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
