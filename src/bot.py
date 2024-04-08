import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardMarkup as Keyboard,
    InlineKeyboardButton as KeyBtn,
)

from logger import logger
from models import Job
from storage import jobs
from client import UpworkRSSClient
from config import cfg
from gpt import translator


class Btn(KeyBtn):
    def __init__(self, job, text):
        super().__init__(
            text=text,
            callback_data=f"{text.lower()}__{job.id}"
        )


class TeleBot:
    bot: Bot = Bot(cfg.upwork_bot_token, parse_mode=ParseMode.HTML)
    client: UpworkRSSClient
    dispatcher: Dispatcher = Dispatcher()

    def __init__(self, app, ):
        self.client = app.rss

    async def serve(self):
        return await self.dispatcher.start_polling(
            self.bot,
            handle_signals=False,
        )

    @staticmethod
    @dispatcher.callback_query()
    async def process_callback(callback_query: types.CallbackQuery):
        name, id = callback_query.data.split("__")

        text = jobs[id].description
        if name == "translate":
            text = translator.translate(text)

        await TeleBot.bot.answer_callback_query(callback_query.id)
        await TeleBot.bot.send_message(callback_query.from_user.id, text)

    @staticmethod
    @dispatcher.message(CommandStart())
    async def _start(message: types.Message):
        user = message.from_user
        cfg.add_user_id(user.id)
        logger.info(f"User {user.username} started the conversation.\n{user}")
        await message.reply("Hello! Welcome to the Upwork bot.")

    async def send_message(self, job: Job):
        logger.info(f"  - Sending '{job.title}'")
        await asyncio.gather(*[self.send_to_user(id, job)
                               for id in cfg.chat_ids])

    async def send_to_user(self, chat_id: str, job: Job):
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=job.get_message(),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=Keyboard(
                    inline_keyboard=[
                        [Btn(job, "Translate"), Btn(job, "Expand")]
                    ]
                ),
            )
        except Exception as e:
            logger.error(f"Error sending message to {chat_id} {e}")

    async def send_job(self, job: Job):
        await self.send_message(job)
