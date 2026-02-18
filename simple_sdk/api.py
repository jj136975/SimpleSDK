import asyncio
from typing import Any, TypeVar, Sequence, TYPE_CHECKING, Coroutine

import serde
from aiohttp import ClientSession, hdrs, payload
from aiohttp.typedefs import StrOrURL, Query
from aiohttp.web_exceptions import HTTPRequestTimeout, HTTPGatewayTimeout
from serde import SerdeError, from_dict

from .errors import InvalidStatus, Timeout, EncodeError, DecodeError, ApiError

T = TypeVar("T")

if TYPE_CHECKING:
    from aiohttp.client import _RequestOptions


    class RetryOptions(_RequestOptions):
        """Options for retrying HTTP requests."""

        retry_status: int | Sequence[int]
        """HTTP status codes that should trigger a retry (default: 500)."""

        max_retries: int
        """The maximum number of retries before giving up (default: 3)."""

        retry_delay: float
        """The delay in seconds between retries (default: 2)."""

_BAD_REQUEST_STATUS = range(400, 500)  # HTTP status codes for client errors (4xx)


class BaseApi:
    """
    Base class for API clients.
    """

    def __init__(self, session: ClientSession, default_error_model: type[Any] = dict):
        """
        Initialize the API client with an API key.

        :param session: The aiohttp ClientSession to use for making requests.
        """
        self._session = session
        self._default_error_model = default_error_model

    if TYPE_CHECKING:
        from typing import Unpack

        async def request(self, method: str, url: StrOrURL, model: type[T], **kwargs: Unpack[RetryOptions]) -> T:
            """
                Make an HTTP request with automatic retries and error handling.

            :param method: HTTP method (e.g., 'GET', 'POST').
            :param url: The URL to send the request to.
            :param model: The type to deserialize the response into.
            :param kwargs: Additional keyword arguments for retry options:
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: 500).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The delay in seconds between retries (default: 2).
            :return: An instance of type T deserialized from the JSON response.
            """
            ...

        def get(self, endpoint: str, params: Query | None = None, model: type[T] = dict,
                **kwargs: Unpack[RetryOptions]) -> Coroutine[Any, Any, T]:
            """
                Make a GET request to the specified endpoint with automatic retries and error handling.
            :param endpoint: The API endpoint to send the GET request to.
            :param params: Optional query parameters to include in the request.
            :param model: The type to deserialize the response into.
            :param kwargs: Additional keyword arguments for retry options:
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: 500).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The delay in seconds between retries (default: 2).
            :return: An instance of type T deserialized from the JSON response.
            """
            ...

        def post(self, endpoint: str, json: Any, model: type[T] = dict, **kwargs: Unpack[RetryOptions]) -> Coroutine[
            Any, Any, T]:
            """
                Make a POST request to the specified endpoint with automatic retries and error handling.
            :param endpoint: The API endpoint to send the POST request to.
            :param json: The JSON payload to include in the POST request.
            :param model: The type to deserialize the response into.
            :param kwargs: Additional keyword arguments for retry options:
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: 500).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The delay in seconds between retries (default: 2).
            :return: An instance of type T deserialized from the JSON response.
            """
            ...

        def put(self, endpoint: str, json: Any, model: type[T] = dict, **kwargs: Unpack[RetryOptions]) -> Coroutine[
            Any, Any, T]:
            """
                Make a PUT request to the specified endpoint with automatic retries and error handling.
            :param endpoint: The API endpoint to send the PUT request to.
            :param json: The JSON payload to include in the PUT request.
            :param model: The type to deserialize the response into.
            :param kwargs: Additional keyword arguments for retry options:
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: 500).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The delay in seconds between retries (default: 2).
            :return: An instance of type T deserialized from the JSON response.
            """
            ...
    else:
        async def request(
                self,
                method: str,
                url: StrOrURL,
                model: type[T],
                *,
                json: Any = None,
                data: Any = None,
                retry_status: int | Sequence[int] = 500,
                max_retries: int = 3,
                retry_delay: float = 2,
                **kwargs: Any
        ) -> T:
            if json is not None:
                try:
                    data = payload.JsonPayload(json, dumps=self._session.json_serialize)
                except SerdeError as e:
                    raise EncodeError(f"Failed to encode JSON payload: {e}", type(json)) from e

            error: Exception | None = None
            while True:
                try:
                    async with self._session.request(method, url, data=data, **kwargs) as response:
                        status = response.status

                        if status == 200 or status == 201:
                            try:
                                return await response.json(loads=lambda obj: serde.json.from_json(model, obj))
                            except SerdeError as e:
                                raise DecodeError(f"Failed to decode JSON response: {e}", await response.text(),
                                                  model) from e
                        elif (isinstance(retry_status, Sequence) and status in retry_status) or status == retry_status:
                            if max_retries <= 0:
                                if status in _BAD_REQUEST_STATUS:
                                    error_data = await response.json()
                                    try:
                                        api_error = from_dict(self._default_error_model, error_data)
                                        error = ApiError(api_error, status)
                                    except SerdeError:
                                        error = DecodeError(f"Failed to decode error response: {error_data}",
                                                            error_data, self._default_error_model)
                                else:
                                    error = InvalidStatus(await response.text(), status)
                                break
                            max_retries -= 1
                            await asyncio.sleep(retry_delay)
                        elif status in _BAD_REQUEST_STATUS:
                            error_data = await response.json()
                            try:
                                api_error = from_dict(self._default_error_model, error_data)
                                error = ApiError(api_error, status)
                            except SerdeError:
                                error = DecodeError(f"Failed to decode error response: {error_data}", error_data,
                                                    self._default_error_model)
                            break
                        else:
                            error = InvalidStatus(await response.text(), status)
                            break
                except HTTPRequestTimeout or HTTPGatewayTimeout as e:
                    error = Timeout(f"Request to {url} timed out: {e}")
                    if max_retries <= 0:
                        break
                    max_retries -= 1
                    await asyncio.sleep(retry_delay)
            assert error is not None
            raise error

        def get(self, endpoint: str, params: Query | None = None, model: type[T] = dict, **kwargs: Any) -> Coroutine[
            Any, Any, T]:
            return self.request(hdrs.METH_GET, endpoint, model, params=params, **kwargs)

        def post(self, endpoint: str, json: Any, model: type[T] = dict, **kwargs: Any) -> Coroutine[Any, Any, T]:
            return self.request(hdrs.METH_POST, endpoint, model, json=json, **kwargs)

        def put(self, endpoint: str, json: Any, model: type[T] = dict, **kwargs: Any) -> Coroutine[Any, Any, T]:
            return self.request(hdrs.METH_PUT, endpoint, model, json=json, **kwargs)
