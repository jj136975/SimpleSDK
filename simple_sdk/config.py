from dataclasses import dataclass, field

DEFAULT_AUTH_URL = "https://login.salesforce.com"


@dataclass(frozen=True)
class BaseConfiguration:
    """Base configuration for API clients."""

    base_url: str
    """Root URL for the API (e.g., 'https://api.example.com/v1')."""

    headers: dict[str, str] = field(default_factory=dict)
    """Default headers to include in every request (e.g., {'Accept': 'application/json'})."""

    agent: str = 'HTTP SDK/python'
    """User-Agent string to identify the client (default: 'HTTP SDK/python')."""
