from time import monotonic

import asyncio
import aiohttp

from bot import TeleBot
from storage import jobs
from client import UpworkRSSClient
from config import cfg
from gpt import Translator
from logger import logger, init_logger


class App:
    rss: UpworkRSSClient
    bot: TeleBot
    translator: Translator

    def __init__(self):
        self.rss = UpworkRSSClient()
        self.translator = Translator()
        self.bot = TeleBot(self)
        init_logger(self.bot)

    def run(self):
        try:
            asyncio.run(self._run())
        except Exception as e:
            logger.error(f"Critical error: {e}")

    async def _run(self):
        logger.info("Starting parser")
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(self._serve(session), self.bot.serve())

    @logger.catch()
    async def _serve(self, session):
        '''Run cycle every {cfg.parse_timeout} seconds'''
        while True:
            try:
                print(f"{cfg.started=}")
                if cfg.started:
                    parse_time = await self._run_cycle(session)
                    logger.info(f"Parsed for {parse_time} secs")
                else:
                    parse_time = 0

                if (to_sleep := cfg.parse_timeout - parse_time) > 0:
                    logger.info(f"Sleeping for {to_sleep}")
                    await asyncio.sleep(to_sleep)
            except Exception as e:
                logger.error(f"Cycle error: {e}")

    @logger.catch()
    async def _run_cycle(self, session):
        '''Returns elapsed time in seconds'''
        t0 = monotonic()

        current_jobs = await self.rss.get_feed(session)
        new_jobs = jobs.get_new(current_jobs)
        logger.debug(f"  - New jobs: {len(new_jobs)} sending last 5")
        for job in new_jobs[:5]:
            await self.bot.send_job(job)
        return monotonic() - t0


if __name__ == '__main__':
    App().run()
