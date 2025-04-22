from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.db_provider import get_db
from utils.book import Booking

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
    database = get_db()
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
    awbs = await database.get_awbs('awb', user_id)

    for i in range(pg * 10, len(awbs)):
        if len(btn) > 10:
            break
        btn.append(types.InlineKeyboardButton(
            text = awbs[i],
            callback_data=awbs[i])
        )
        if k == len(awbs):
            history_builder.row(btn[-1])
        if k % 2 == 0:
            history_builder.row(btn[-2], btn[-1])
        k+=1
    history_builder.row(prev_btn, close_btn, next_btn)
    
    return history_builder.as_markup()

async def get_info(awb, user_id):
    database = get_db()
    awb_info_builder = InlineKeyboardBuilder()
    close_btn = types.InlineKeyboardButton(
            text = '❌',
            callback_data='prev_pg')
    flight = await database.get_awb_info('flight', awb, user_id)
    date = await database.get_awb_info('date', awb, user_id)
    booking_status = await database.get_awb_info('booking_status', awb, user_id)
    arrival_status = await database.get_awb_info('arrival_status', awb, user_id)
    flight_btn = types.InlineKeyboardButton(
            text = f"{flight}/{date}: {booking_status}",
            callback_data='1')

    arrival_btn = types.InlineKeyboardButton(
            text = f'{arrival_status}',
            callback_data='2')
    
    awb_info_builder.row(flight_btn)
    awb_info_builder.row(arrival_btn)
    awb_info_builder.row(close_btn)
    return awb_info_builder.as_markup()

async def get_flights(departure, destination, date, aircrafts = ['73H', '77W'], pg = 0):
    database = get_db()
    flights = await database.get_available_flights(date, departure, destination)
    flights_builder = InlineKeyboardBuilder()
    close_btn = types.InlineKeyboardButton(
            text = '❌',
            callback_data='prev_pg')
    next_btn = types.InlineKeyboardButton(
            text = '➡️',
            callback_data='next_pg')
    prev_btn = types.InlineKeyboardButton(
            text = '⬅️',
            callback_data='prev_pg')
    btn = []
    k = 1
    for i in range(pg * 10, len(flights)):
        if len(btn) > 10:
            break
        btn.append(types.InlineKeyboardButton(
            text = flights[i][0],
            callback_data=str(flights[i][0]))
        )
        if k == len(flights):
            flights_builder.row(btn[-1])
        if k % 2 == 0:
            flights_builder.row(btn[-2], btn[-1])
        k+=1
    flights_builder.row(close_btn)
    
    return flights_builder.as_markup()

async def get_change_awb(awb, user_id):
    database = get_db()
    change_awb_builder = InlineKeyboardBuilder()
    try:
        pcs = await database.get_awb_info('pieces', awb, user_id)
        w = await database.get_awb_info('weight', awb, user_id)
        v = await database.get_awb_info('volume', awb, user_id)
        cargo = await database.get_awb_info('cargo', awb, user_id)
        fr = await database.get_awb_info('departure', awb, user_id)
        dest = await database.get_awb_info('destination', awb, user_id)
        flight = await database.get_awb_info('flight', awb, user_id)
        date = await database.get_awb_info('date', awb, user_id)
        client = await database.get_awb_info('client', awb, user_id)
    except:
        print('failed to get change awb')
        fail_btn = (types.InlineKeyboardButton(
            text = '❌NO SUCH AWB❌',
            callback_data='close'))
        change_awb_builder.row(fail_btn)
        return change_awb_builder.as_markup()

    change_awb_builder = InlineKeyboardBuilder()

    close_btn = types.InlineKeyboardButton(
            text = '❌',
            callback_data='close')
    
    go_btn = types.InlineKeyboardButton(
            text = '✅',
            callback_data='go')
    
    pcs_btn = (types.InlineKeyboardButton(
            text = f'pcs: {pcs}',
            callback_data='pieces'
    ))

    weight_btn = (types.InlineKeyboardButton(
            text = f'weight: {w}',
            callback_data='weight'
    ))

    vol_btn = (types.InlineKeyboardButton(
            text = f'volume: {v}',
            callback_data='volume'
    ))

    cargo_btn = (types.InlineKeyboardButton(
            text = f'cargo: {cargo}',
            callback_data='cargo'
    ))

    fr_btn = (types.InlineKeyboardButton(
            text = f'from: {fr}',
            callback_data='departure'
    ))

    dest_btn = (types.InlineKeyboardButton(
            text = f'to: {dest}',
            callback_data='destination'
    ))

    flight_btn = (types.InlineKeyboardButton(
            text = f'flight: {flight}',
            callback_data='flight'
    ))
    date_btn = (types.InlineKeyboardButton(
            text = f'date: {date}',
            callback_data='date'
    ))
    client_btn = (types.InlineKeyboardButton(
            text = f'client: {client}',
            callback_data='client'
    ))

    change_awb_builder.row(pcs_btn, weight_btn)
    change_awb_builder.row(vol_btn, cargo_btn)
    change_awb_builder.row(fr_btn, dest_btn)
    change_awb_builder.row(flight_btn, date_btn)
    change_awb_builder.row(client_btn)
    change_awb_builder.row(close_btn, go_btn)

    return change_awb_builder.as_markup()

async def set_client():
    client_builder = InlineKeyboardBuilder()
    close_btn = types.InlineKeyboardButton(
            text = '❌',
            callback_data='close')
    limit_btn = types.InlineKeyboardButton(
            text = 'Limittrans',
            callback_data='Limittrans')
    routas_btn = types.InlineKeyboardButton(
            text = 'Turkish log',
            callback_data='Turkish Logistic')
    
    client_builder.row(limit_btn, routas_btn)
    client_builder.row(close_btn)

    return client_builder.as_markup()