import asyncio
import base64
import random

import aiohttp
import uvloop
import web3
from structlog import get_logger
from structlog.types import BindableLogger

from src.config import AppConfig, Config
from src.exceptions.base import ApplicationError
from src.exceptions.openledger import OpenledgerAPIError


async def main() -> None:
    logger = get_logger()
    try:
        config = AppConfig()
        await run(config, logger)
    except ApplicationError as _ex:
        await logger.aerror(_ex.message)


async def run(config: Config, logger: BindableLogger) -> None:
    proxies_path = config.proxies_path()
    if not proxies_path:
        return await process(config, logger)
    proxies = proxies_path.read_text("utf-8").split("\n")[:-1]
    await asyncio.gather(
        *[asyncio.create_task(process(config, logger, proxy)) for proxy in proxies],
    )


async def process(
    config: Config,
    logger: BindableLogger,
    proxy: str | None = None,
) -> None:
    session = await create_session(config, proxy)
    uri = f"{config.ws_uri()}?authToken={config.token()}"
    address = await wallet(session, config)
    identity = base64.b64encode(address.encode("utf-8")).decode("utf-8")
    while True:
        try:
            await process_ws(uri, identity, address, session, logger)
        except aiohttp.WSServerHandshakeError:
            await logger.awarning(
                "Websocket handshake error. Sleeping for 10 sec. and restart.",
            )
            await asyncio.sleep(10)
            continue


async def create_session(
    config: Config,
    proxy: str | None = None,
) -> aiohttp.ClientSession:
    return aiohttp.ClientSession(
        headers={
            "user-agent": config.user_agent(),
        },
        proxy=proxy,
        connector=aiohttp.TCPConnector(ssl=False),
    )


async def wallet(session: aiohttp.ClientSession, config: Config) -> str:
    response = await session.get(
        f"{config.api_uri()}/users/me",
        headers={"authorization": f"Bearer {config.token()}"},
    )
    if response.status != 200:
        raise OpenledgerAPIError(
            OpenledgerAPIError.message.format(response.status),
        )
    json_data = await response.json()
    return web3.Web3().to_checksum_address(json_data["data"]["address"])


async def process_ws(
    uri: str,
    identity: str,
    address: str,
    session: aiohttp.ClientSession,
    logger: BindableLogger,
) -> None:
    await logger.awarning("Opening connection")
    async with session.ws_connect(uri) as ws:
        while True:
            heartbeat = {
                "message": {
                    "Worker": {
                        "Identity": identity,
                        "ownerAddress": address,
                        "type": "LWEXT",
                        "Host": "chrome-extension://ekbbplmjjgoobhdlffmgeokalelnmjjc",
                    },
                    "Capacity": {
                        "AvailableMemory": round(random.uniform(35, 44), 2),
                        "AvailableStorage": "99.03",
                        "AvailableGPU": "",
                        "AvailableModels": [],
                    },
                },
                "msgType": "HEARTBEAT",
                "workerType": "LWEXT",
                "workerID": identity,
            }
            try:
                await ws.send_json(heartbeat)
            except (
                aiohttp.ClientConnectionResetError,
            ):
                break
            await logger.ainfo(f"Sent -> {heartbeat}")
            await logger.ainfo("sleeping")
            await asyncio.sleep(30)


if __name__ == "__main__":
    uvloop.run(main())
