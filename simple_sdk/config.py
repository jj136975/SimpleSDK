from dataclasses import dataclass, field

DEFAULT_AUTH_URL = "https://login.salesforce.com"


@dataclass(frozen=True)
class BaseConfiguration:
    """Base configuration for API clients."""
    base_url: str
    headers: dict[str, str] = field(default_factory=dict)
    agent: str = 'HTTP SDK/python'
