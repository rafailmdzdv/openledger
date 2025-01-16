from src.exceptions.base import ApplicationError


class TokenNotFoundError(ApplicationError):
    message = "Provide user auth token in configruation."


class OpenledgerApiURINotFoundError(ApplicationError):
    message = "Openledger API URI not found. Don't delete it in future."


class OpenledgerWsURINotFoundError(ApplicationError):
    message = "Openledger WS URI not found. Don't delete it in future."


class UserAgentNotFoundError(ApplicationError):
    message = "User agent not found in config. Don't delete it in future."
