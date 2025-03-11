import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.client.default import DefaultBotProperties
from aiogram import F
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from handlers import booking_h

from aiogram.fsm.context import FSMContext
import os
load_dotenv()

class Reservation():
    def __init__(self):
        bot_token = os.getenv('BOT_TOKEN')
        logging.basicConfig(level=logging.INFO)
        self.bot = Bot(token=bot_token, default=DefaultBotProperties(
                )
                )
        self.dp = Dispatcher()
        self.dp.include_routers(booking_h.router)

    async def logic(self):
        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            await message.answer(
                "Hello, this is an official Tesis cargo booking system. Please send your FFR message here"
            )

    async def main(self):
        await self.logic()
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

if __name__ == "__main__":
    bot = Reservation()
    asyncio.run(bot.main())
