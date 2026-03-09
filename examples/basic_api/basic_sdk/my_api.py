from aiohttp import ClientSession

from simple_sdk.api import BaseApi

from .models import MyApiError, MyProfile


class MyApi(BaseApi):
    def __init__(self, session: ClientSession) -> None:
        super().__init__(session, default_error_model=MyApiError)

    async def get_my_profile(self) -> MyProfile:
        """
        Get the user's profile information.

        :return: An instance of MyProfile containing the user's profile data.
        :raises MyApiError: If the API returns an error response.
        """
        return await self.get("/profile", model=MyProfile)
