from dataclasses import dataclass
from pathlib import Path

import tomllib

from src.config.base import Config
from src.exceptions.config import (
    OpenledgerApiURINotFoundError,
    OpenledgerWsURINotFoundError,
    TokenNotFoundError,
    UserAgentNotFoundError,
)


@dataclass(frozen=True)
class AppConfig(Config):
    _path: Path = Path(__file__).parent.parent.parent / "config.toml"

    def token(self) -> str:
        toml = tomllib.load(self._path.open("rb"))
        if not toml.get("token"):
            raise TokenNotFoundError
        return toml["token"]

    def api_uri(self) -> str:
        toml = tomllib.load(self._path.open("rb"))
        if not toml.get("api_uri"):
            raise OpenledgerApiURINotFoundError
        return toml["api_uri"]

    def ws_uri(self) -> str:
        toml = tomllib.load(self._path.open("rb"))
        if not toml.get("ws_uri"):
            raise OpenledgerWsURINotFoundError
        return toml["ws_uri"]

    def user_agent(self) -> str:
        toml = tomllib.load(self._path.open("rb"))
        if not toml.get("user_agent"):
            raise UserAgentNotFoundError
        return toml["user_agent"]

    def proxies_path(self) -> Path | None:
        toml = tomllib.load(self._path.open("rb"))
        if not toml.get("proxies_path"):
            return None
        return Path(__file__).parent.parent.parent / toml["proxies_path"]
