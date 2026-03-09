from dataclasses import dataclass, field
from typing import Any

from aiohttp import ClientSession, ClientTimeout


@dataclass
class BaseConfiguration:
    """Base configuration for API clients."""

    base_url: str
    """Root URL for the API (e.g., 'https://api.example.com/v1')."""

    headers: dict[str, str] = field(default_factory=dict)
    """Default headers to include in every request (e.g., {'Accept': 'application/json'})."""

    agent: str = 'HTTP SDK/python'
    """User-Agent string to identify the client (default: 'HTTP SDK/python')."""

    timeout: ClientTimeout | None = None
    """Request timeout configuration. If None, aiohttp defaults are used."""

    def create_session(self, **kwargs: Any) -> ClientSession:
        """Create an aiohttp ClientSession with the configured base URL and headers."""
        headers = self.headers.copy()
        headers['User-Agent'] = self.agent
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)
        return ClientSession(
            base_url=self.base_url,
            headers=headers,
            **kwargs,
        )
