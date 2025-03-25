from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from db import Db
from utils.book import Booking

database = Db()

country_builder = InlineKeyboardBuilder()
country_builder.row(types.InlineKeyboardButton(
    text="Turkey",
    callback_data="TURKEY"),
    width = 1
    )
country_builder.row(types.InlineKeyboardButton(
    text="China",
    callback_data="CHINA"),
    width = 1
)

menu_builder = InlineKeyboardBuilder()
menu_builder.row(types.InlineKeyboardButton(
    text="Book",
    callback_data="book"),
    width = 1
    )
menu_builder.row(types.InlineKeyboardButton(
    text="Change booking",
    callback_data="change"),
    width = 1
    )
menu_builder.row(types.InlineKeyboardButton(
    text="Cancel booking",
    callback_data="cancel"),
    width = 1
    )

menu_builder.row(types.InlineKeyboardButton(
    text="Check status",
    callback_data="check"),
    width = 1
    )

menu_builder.row(types.InlineKeyboardButton(
    text="Watch all AWBs",
    callback_data="history"),
    width = 1
    )

confirm_builder = InlineKeyboardBuilder()
confirm_builder.row(types.InlineKeyboardButton(
    text="Continue✅",
    callback_data="ok"),
    width = 1
    )
confirm_builder.row(types.InlineKeyboardButton(
    text="Change🔄",
    callback_data="ch"),
    width = 1
    )
confirm_builder.row(types.InlineKeyboardButton(
    text="Cancel❌",
    callback_data="cn"),
    width = 1
    )

async def get_awb_history(user_id, pg):
    history_builder = InlineKeyboardBuilder()
    next_btn = types.InlineKeyboardButton(
            text = '➡️',
            callback_data='next_pg')
    prev_btn = types.InlineKeyboardButton(
            text = '⬅️',
            callback_data='prev_pg')
    close_btn = types.InlineKeyboardButton(
            text = '❌',
            callback_data='close')

    k = 1
    btn = []
    awbs = database.get_awbs('awb', user_id)
    for i in range(pg * 10, len(awbs)):
        if len(btn) > 10:
            break
        btn.append(types.InlineKeyboardButton(
            text = awbs[i][0],
            callback_data=awbs[i][0])
        )
        if k == len(awbs):
            history_builder.row(btn[-1])
        if k % 2 == 0:
            history_builder.row(btn[-2], btn[-1])
        k+=1
    history_builder.row(prev_btn, close_btn, next_btn)
    
    return history_builder.as_markup()

async def get_info(awb, user_id):
    awb_info_builder = InlineKeyboardBuilder()
    close_btn = types.InlineKeyboardButton(
            text = '❌',
            callback_data='prev_pg')
    flight = database.get_awb_info('flight', awb, user_id)
    date = database.get_awb_info('date', awb, user_id)
    booking_status = database.get_awb_info('booking_status', awb, user_id)
    arrival_status = database.get_awb_info('arrival_status', awb, user_id)
    flight_btn = types.InlineKeyboardButton(
            text = f"{flight[0][0]}/{date[0][0]}: {booking_status[0][0]}",
            callback_data='1')

    arrival_btn = types.InlineKeyboardButton(
            text = f'{arrival_status[0][0]}',
            callback_data='2')
    
    awb_info_builder.row(flight_btn)
    awb_info_builder.row(arrival_btn)
    awb_info_builder.row(close_btn)
    return awb_info_builder.as_markup()

async def get_flights(fr, to, day, month, aircrafts = ['73H', '77W']):
    bk = Booking()
    flights = await bk.available_flghts(fr, to, day, month, aircrafts)
    flights_builder = InlineKeyboardBuilder()
    close_btn = types.InlineKeyboardButton(
            text = '❌',
            callback_data='prev_pg')
    for f in flights:
        flights_builder.add(types.InlineKeyboardButton(
            text = f'{f[0]}/{f[2]}: {f[1]}',
            callback_data=f'{f[0]}/{f[2]}'))
    
    return flights_builder.as_markup()