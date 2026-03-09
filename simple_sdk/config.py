from dataclasses import dataclass, field

from aiohttp import ClientSession


@dataclass
class BaseConfiguration:
    """Base configuration for API clients."""

    base_url: str
    """Root URL for the API (e.g., 'https://api.example.com/v1')."""

    headers: dict[str, str] = field(default_factory=dict)
    """Default headers to include in every request (e.g., {'Accept': 'application/json'})."""

    agent: str = 'HTTP SDK/python'
    """User-Agent string to identify the client (default: 'HTTP SDK/python')."""

    def create_session(self) -> ClientSession:
        headers = self.headers.copy()
        headers['User-Agent'] = self.agent
        """Create an aiohttp ClientSession with the configured base URL and headers."""
        return ClientSession(
            base_url=self.base_url,
            headers=headers,
        )
