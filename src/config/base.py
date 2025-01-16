from pathlib import Path
from typing import Protocol


class Config(Protocol):
    def token(self) -> str:
        """Return user auth token."""

    def api_uri(self) -> str:
        """Return openledger api uri."""

    def ws_uri(self) -> str:
        """Return openledger ws uri."""

    def user_agent(self) -> str:
        """Return user agent."""

    def proxies_path(self) -> Path | None:
        """Return proxies file path."""
