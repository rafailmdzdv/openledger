from dataclasses import dataclass, field

from src.exceptions.base import ApplicationError


@dataclass
class OpenledgerAPIError(ApplicationError):
    message: str = field(default="Openledger API error. Status code: {0}")
