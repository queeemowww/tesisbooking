import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.client.default import DefaultBotProperties
from aiogram import F
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from handlers import booking_h, change_h, cancel_h, check_h, awb_history_h
from kb.booking_kb import menu_builder
from db import Db
from aiogram.fsm.context import FSMContext
import os
from utils.check_arrival import Arrival
from utils.book import Booking
load_dotenv()

class Reservation():
    def __init__(self):
        bot_token = os.getenv('BOT_TOKEN')
        logging.basicConfig(level=logging.INFO)
        self.bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML
                )
                )
        self.dp = Dispatcher()
        self.dp.include_routers(booking_h.router, change_h.router, cancel_h.router, check_h.router, awb_history_h.router)
        self.database = Db()

    async def logic(self):
        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            self.database.insert_user(message.chat.id, message.chat.username, message.chat.first_name, message.chat.last_name)
            self.database.cursor.close()
            await message.delete()
            await message.answer(
                "Hello, this is an official Tesis cargo booking system. Please send your FFR message here", reply_markup=menu_builder.as_markup()
            )

        @self.dp.message(F.text != '/clear', StateFilter(None))
        async def menu(message: types.Message):
            await message.delete()
            await message.answer(
                "Please choose an option", reply_markup=menu_builder.as_markup()
            )
        @self.dp.message(Command("clear"))
        async def cmd_clear(message: types.Message, state:FSMContext):
            await message.delete()
            await message.answer(
                "the context was cleared"
            )
            state.set_state(None)
            
    async def check_arrivals(self, delay):
        while(True):
            try:
                awbs = self.database.get_not_arrived()
                for awb in awbs:
                    self.arrival = Arrival()
                    arrival_status = await self.arrival.is_arrived(awb[0][:3], awb[0][4:])[0]
                    self.database.update_awb(awb[0], ['arrival_status', arrival_status])
                print(f'--------->Checked arrival_status for all awbs, will do it again in {delay} seconds')
            except Exception as e:
                print(e)
                pass
            await asyncio.sleep(delay)

    async def check_booking(self, delay):
        while(True):
            try:
                awbs = self.database.get_not_booked()
                for awb in awbs:
                    self.booking = Booking()
                    booking_status = await self.booking.check(awb = awb[0], auto=True)[0]
                    self.database.update_awb(awb[0], ['booking_status', booking_status])
                print(f'--------->Checked booking_status for all awbs, will do it again in {delay} seconds')
            except Exception as e:
                print(e)
            await asyncio.sleep(delay)


    async def main(self):
        await self.logic()
        asyncio.create_task(self.check_arrivals(3600))
        asyncio.create_task(self.check_booking(3600))
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

if __name__ == "__main__":
    bot = Reservation()
    asyncio.run(bot.main())
