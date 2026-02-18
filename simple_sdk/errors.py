class ClientError(Exception):
    """API Request Error."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ApiError[T](ClientError):
    def __init__(self, error: T, status: int):
        super().__init__(f"API Error with status {status}: {error}")
        self._error = error
        self._status = status

    def __str__(self) -> str:
        return f"API Error (status: {self._status}): error: {self._error}"

    def __repr__(self) -> str:
        return f"ApiError(status={self._status}, error={self._error})"


class EncodeError(ClientError):
    """Error during JSON encoding."""

    def __init__(self, message: str, cls: type):
        super().__init__(message)
        self._cls = cls

    @property
    def cls(self) -> type: return self._cls

    def __str__(self) -> str:
        return f"Failed to encode object '{self.cls}' to JSON: {self.message}"

    def __repr__(self) -> str:
        return f"EncodeError(cls={self.cls}, message={self.message})"


class DecodeError(ClientError):
    """Error during JSON decoding."""

    def __init__(self, message: str, payload: str, cls: type):
        super().__init__(message)
        self._payload = payload
        self._cls = cls

    @property
    def payload(self) -> str: return self._payload

    @property
    def cls(self) -> type: return self._cls

    def __str__(self) -> str:
        return f"Failed to decode JSON to object '{self.cls}': {self.message}, payload: {self.payload}"

    def __repr__(self) -> str:
        return f"DecodeError(cls={self.cls}, payload={self.payload}, message={self.message})"


class InvalidStatus(ClientError):
    def __init__(self, message: str, status: int, ):
        super().__init__(message)
        self._status = status

    @property
    def status(self) -> int: return self._status

    def __str__(self) -> str:
        return f"Invalid Status: {self._status}, message: {self.message}"

    def __repr__(self) -> str:
        return f"InvalidStatus(status={self._status}, message={self.message})"


class Timeout(ClientError):
    """Timeout error."""

    def __init__(self, message: str, timeout_seconds: float = 0):
        super().__init__(message)
        self._timeout = timeout_seconds

    @property
    def timeout(self) -> float: return self._timeout

    def __str__(self) -> str:
        return f"Exceeded Timeout ({self.timeout} s): {self.message}"

    def __repr__(self) -> str:
        return f"Timeout(timeout={self.timeout} s, message={self.message})"
