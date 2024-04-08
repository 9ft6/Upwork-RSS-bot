import asyncio

import aiohttp

from config import cfg
from logger import logger


class BaseWebClient:
    session: aiohttp.ClientSession
    headers: dict = {}

    def __init__(self, session: aiohttp.ClientSession = None):
        if session:
            self.session = session

    async def make_request(self, url, method="GET",
                           attempts=cfg.request_attempts, **kwargs):
        while attempts:
            try:
                async with self.session.request(
                        method,
                        url,
                        headers=self.headers,
                        **kwargs
                ) as response:
                    # logger.debug(f"{url}: {response.status=}")
                    if response.status >= 400:
                        return await response.read(), response.status
                    if response.status >= 300:
                        logger.warning(f"{url}: got a {response.status} "
                                       f"response code {await response.read()}")
                        attempts -= 1
                        return await self.make_request(
                            url,
                            method=method,
                            attempts=attempts,
                            **kwargs,
                        )

                    try:
                        result = await response.text()
                    except Exception as e:
                        logger.error(f"Can not read text: {e}")
                        result = await response.read()

                    # logger.debug(f"{url}: RESPONSE BODY: {result}")
                    return result, response.status
            except aiohttp.InvalidURL as error:
                logger.error(f"{url}: Invalid url: {error}")
                return None, None
            except aiohttp.ClientPayloadError as error:
                logger.error(f"{url}: Malformed payload: {error}")
                return None, None
            except (
                aiohttp.ClientConnectorError,
                aiohttp.ClientOSError,
                aiohttp.ClientResponseError,
                aiohttp.ServerDisconnectedError,
                asyncio.TimeoutError,
                ValueError,
            ) as error:
                attempts -= 1
                logger.warning(
                    f"{url}: Got an error {error} during GET request"
                )
                if not attempts:
                    break

                return await self.make_request(
                    url,
                    method=method,
                    attempts=attempts,
                    **kwargs
                )

        logger.error(
            f"{url}: Exceeded the number of attempts "
            f"to perform {method.upper()} request")
        return None, None
