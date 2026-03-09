import asyncio
import random
from dataclasses import dataclass
from typing import Any, TypeVar, Sequence, TYPE_CHECKING, Coroutine

import serde
from aiohttp import ClientSession, ClientResponse, hdrs, payload
from aiohttp.typedefs import StrOrURL, Query
from serde import SerdeError, from_dict

from .errors import InvalidStatus, Timeout, EncodeError, DecodeError, ApiError

T = TypeVar("T")

if TYPE_CHECKING:
    from aiohttp.client import _RequestOptions


    class RetryOptions(_RequestOptions, total=False):
        """Options for retrying HTTP requests."""

        retry_status: int | Sequence[int]
        """HTTP status codes that should trigger a retry (default: (500, 502, 503, 504))."""

        max_retries: int
        """The maximum number of retries before giving up (default: 3)."""

        retry_delay: float
        """The base delay in seconds between retries, with exponential backoff (default: 2)."""

_BAD_REQUEST_STATUS = range(400, 500)  # HTTP status codes for client errors (4xx)


@dataclass
class Retry:
    """Return from on_status to retry the request without counting against max_retries."""
    delay: float | None = None
    """Override the retry delay in seconds. If None, uses the request's retry_delay."""


@dataclass
class Raise:
    """Return from on_status to immediately raise an error."""
    error: Exception


class BaseApi:
    """
    Base class for API clients.
    """

    _SUCCESS_STATUS: frozenset[int] = frozenset({200, 201})
    """HTTP status codes treated as success. Override in subclasses to add e.g. 204."""

    def __init__(self, session: ClientSession, default_error_model: type[Any] = dict):
        """
        Initialize the API client.

        :param session: The aiohttp ClientSession to use for making requests.
        :param default_error_model: The type to deserialize error responses into.
        """
        self._session = session
        self._default_error_model = default_error_model

    async def on_status(self, status: int, response: ClientResponse) -> Retry | Raise | None:
        """
        Hook for subclasses to handle specific HTTP status codes.

        Called for every response whose status is not in _SUCCESS_STATUS, before the
        default retry/error logic runs. Override in subclasses to customize behavior
        for specific status codes (e.g. 202 Request Not Ready, 429 Rate Limit).

        :param status: The HTTP status code.
        :param response: The aiohttp response object (body can be read).
        :return: Retry to retry without counting against max_retries,
                 Raise to immediately raise an error, or None for default handling.
        """
        return None

    if TYPE_CHECKING:
        from typing import Unpack

        async def request(self, method: str, url: StrOrURL, model: type[T], **kwargs: Unpack[RetryOptions]) -> T:
            """
                Make an HTTP request with automatic retries and error handling.

            :param method: HTTP method (e.g., 'GET', 'POST').
            :param url: The URL to send the request to.
            :param model: The type to deserialize the response into.
            :param kwargs: Additional keyword arguments for retry options:
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: (500, 502, 503, 504)).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The base delay in seconds between retries, with exponential backoff (default: 2).
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
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: (500, 502, 503, 504)).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The base delay in seconds between retries, with exponential backoff (default: 2).
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
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: (500, 502, 503, 504)).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The base delay in seconds between retries, with exponential backoff (default: 2).
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
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: (500, 502, 503, 504)).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The base delay in seconds between retries, with exponential backoff (default: 2).
            :return: An instance of type T deserialized from the JSON response.
            """
            ...

        def delete(self, endpoint: str, params: Query | None = None, model: type[T] = dict,
                   **kwargs: Unpack[RetryOptions]) -> Coroutine[Any, Any, T]:
            """
                Make a DELETE request to the specified endpoint with automatic retries and error handling.
            :param endpoint: The API endpoint to send the DELETE request to.
            :param params: Optional query parameters to include in the request.
            :param model: The type to deserialize the response into.
            :param kwargs: Additional keyword arguments for retry options:
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: (500, 502, 503, 504)).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The base delay in seconds between retries, with exponential backoff (default: 2).
            :return: An instance of type T deserialized from the JSON response.
            """
            ...

        def patch(self, endpoint: str, json: Any, model: type[T] = dict, **kwargs: Unpack[RetryOptions]) -> Coroutine[
            Any, Any, T]:
            """
                Make a PATCH request to the specified endpoint with automatic retries and error handling.
            :param endpoint: The API endpoint to send the PATCH request to.
            :param json: The JSON payload to include in the PATCH request.
            :param model: The type to deserialize the response into.
            :param kwargs: Additional keyword arguments for retry options:
                - retry_status: An int or a sequence of ints representing HTTP status codes that should trigger a retry (default: (500, 502, 503, 504)).
                - max_retries: The maximum number of retries before giving up (default: 3).
                - retry_delay: The base delay in seconds between retries, with exponential backoff (default: 2).
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
                retry_status: int | Sequence[int] = (500, 502, 503, 504),
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
            attempt = 0
            while True:
                try:
                    async with self._session.request(method, url, data=data, **kwargs) as response:
                        status = response.status

                        if status in self._SUCCESS_STATUS:
                            try:
                                return await response.json(loads=lambda obj: serde.json.from_json(model, obj))
                            except SerdeError as e:
                                raise DecodeError(f"Failed to decode JSON response: {e}", await response.text(),
                                                  model) from e

                        directive = await self.on_status(status, response)
                        if isinstance(directive, Retry):
                            await asyncio.sleep(directive.delay if directive.delay is not None else retry_delay)
                            continue
                        elif isinstance(directive, Raise):
                            error = directive.error
                            break

                        if (isinstance(retry_status, Sequence) and status in retry_status) or status == retry_status:
                            if attempt >= max_retries:
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
                            attempt += 1
                            await asyncio.sleep(retry_delay * (2 ** (attempt - 1)) + random.uniform(0, 1))
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
                except asyncio.TimeoutError as e:
                    error = Timeout(f"Request to {url} timed out: {e}")
                    if attempt >= max_retries:
                        break
                    attempt += 1
                    await asyncio.sleep(retry_delay * (2 ** (attempt - 1)) + random.uniform(0, 1))
            if error is None:
                raise RuntimeError("Request loop completed without producing a result or error")
            raise error

        def get(self, endpoint: str, params: Query | None = None, model: type[T] = dict, **kwargs: Any) -> Coroutine[
            Any, Any, T]:
            return self.request(hdrs.METH_GET, endpoint, model, params=params, **kwargs)

        def post(self, endpoint: str, json: Any, model: type[T] = dict, **kwargs: Any) -> Coroutine[Any, Any, T]:
            return self.request(hdrs.METH_POST, endpoint, model, json=json, **kwargs)

        def put(self, endpoint: str, json: Any, model: type[T] = dict, **kwargs: Any) -> Coroutine[Any, Any, T]:
            return self.request(hdrs.METH_PUT, endpoint, model, json=json, **kwargs)

        def delete(self, endpoint: str, params: Query | None = None, model: type[T] = dict, **kwargs: Any) -> \
                Coroutine[Any, Any, T]:
            return self.request(hdrs.METH_DELETE, endpoint, model, params=params, **kwargs)

        def patch(self, endpoint: str, json: Any, model: type[T] = dict, **kwargs: Any) -> Coroutine[Any, Any, T]:
            return self.request(hdrs.METH_PATCH, endpoint, model, json=json, **kwargs)
