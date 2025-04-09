import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from handlers import booking_h, change_h, cancel_h, check_h, awb_history_h
from kb.booking_kb import menu_builder
from database.db import Db
from database.db_provider import set_db_instance
from aiogram.fsm.context import FSMContext
import os
from utils.check_arrival import Arrival
from utils.book import Booking
import datetime

load_dotenv()
ADMIN_ID = os.getenv('ADMIN_ID')

departure = ['AYT', 'IST']

class Reservation:
    def __init__(self):
        bot_token = os.getenv('BOT_TOKEN')
        logging.basicConfig(level=logging.INFO)

        self.bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        self.dp.include_routers(
            booking_h.router, change_h.router, cancel_h.router, check_h.router, awb_history_h.router
        )

        self.arrival = Arrival()
        self.booking = Booking()

    async def setup_handlers(self):
        self.database = Db()
        await self.database.init()
        set_db_instance(self.database)

        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):

            if str(message.chat.id) != ADMIN_ID:
                 await message.answer("You seem to be a stranger, ?huh? 🧌")
                 return
            else:
                await self.database.insert_user(
                    str(message.chat.id),
                    str(message.chat.username),
                    str(message.chat.first_name),
                    str(message.chat.last_name)
                )
                await message.delete()
                await message.answer(
                    "Hello, this is an official Tesis cargo booking system. Please choose an option below",
                    reply_markup=menu_builder.as_markup()
                )

        @self.dp.message(Command("clear"))
        async def cmd_clear(message: types.Message, state: FSMContext):

            if str(message.chat.id) != ADMIN_ID:
                 await message.answer("You seem to be a stranger, ?huh? 🧌")
                 return
            else:
                await message.delete()
                await message.answer("The context was cleared")
                await state.clear()

        @self.dp.message(F.text != "/clear", StateFilter(None))
        async def menu(message: types.Message):

            if str(message.chat.id) != ADMIN_ID:
                 await message.answer("You seem to be a stranger, ?huh? 🧌")
                 return

            else:
                await message.delete()
                await message.answer(
                    "Please choose an option",
                    reply_markup=menu_builder.as_markup()
                )

    async def check_arrivals(self, delay):
        while True:
            try:
                awbs = await self.database.get_not_arrived()
                for awb in awbs:
                    arrival_status = await self.arrival.is_arrived(awb=awb)
                    await self.database.update_awb(awb[0], ['arrival_status', arrival_status[0]])
                print(f"[ARRIVALS] Checked arrival_status for all awbs. Next check in {delay}s")
            except Exception as e:
                print(f"[ARRIVALS ERROR] {e}")
            await asyncio.sleep(delay)

    async def check_booking(self, delay):
        while True:
            try:
                awbs = await self.database.get_not_booked()
                for awb in awbs:
                    booking_status = await self.booking.check(awb=awb)
                    await self.database.update_awb(awb[0], ['booking_status', booking_status[0]])
                print(f"[BOOKING] Checked booking_status for all awbs. Next check in {delay}s")
            except Exception as e:
                print(f"[BOOKING ERROR] {e}")
            await asyncio.sleep(delay)

    async def check_available_flights(self, delay):
        while True:
            today = datetime.date.today()
            try:
                for dep in departure:
                    for i in range(10):
                        tomorrow = today + datetime.timedelta(days=i)
                        flights = await self.booking.available_flights(dep, 'SVO', str(tomorrow)[-2:], 'ND')
                        for f in flights:
                            await self.database.ins_upd_available_flight(str(datetime.datetime.now()), f[0], dep, 'SVO', f[2], f[1])
                print(f"[FLIGHTS] Updated available flights. Next update in {delay}s")
            except Exception as e:
                print(f"[FLIGHTS ERROR] {e}")
            await asyncio.sleep(delay)

    async def main(self):
        await self.setup_handlers()
        await self.bot.delete_webhook(drop_pending_updates=True)

        # Запускаем фоновую работу в фоне
        background_tasks = [
            # asyncio.create_task(self.check_arrivals(3600)),
            asyncio.create_task(self.check_booking(3600)),
            # asyncio.create_task(self.check_available_flights(3600)),
        ]

        # dp.start_polling держит event loop активным
        try:
            await self.dp.start_polling(self.bot)
        finally:
            for task in background_tasks:
                task.cancel()
            await asyncio.gather(*background_tasks, return_exceptions=True)

if __name__ == "__main__":
    bot = Reservation()
    asyncio.run(bot.main())
