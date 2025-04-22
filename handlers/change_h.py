from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram import F
from aiogram.fsm.context import FSMContext
from utils.isffr import is_ffr, get_info
from utils.book import Booking
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command, StateFilter
from states.booking_states import Change_states, Change_states
import os
from kb.booking_kb import confirm_builder, menu_builder, country_builder, get_change_awb, get_flights
import re
from database.db_provider import get_db
import asyncio

router = Router()
prev = {}
awb = {}
change_val = {}
pg = {}

awb_pattern = "^555-\d{8}$"

@router.callback_query(F.data == "change", StateFilter(None))
async def book_01(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>AWB</b> 11 digits separated with -')
    await state.set_state(Change_states.awb)

@router.message(StateFilter(Change_states.awb))
async def book_02(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    if re.match(awb_pattern, message.text):
        awb[message.chat.id] = message.text
        prev[message.chat.id] = await message.answer('AWB: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer("Incorrect awb format")
        await message.delete()
@router.callback_query(F.data == "ch", StateFilter(Change_states.awb))
async def book_03(callback: types.CallbackQuery, state: FSMContext):
    await prev[callback.message.chat.id].delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>AWB</b> 11 digits separated with -)')

@router.callback_query(F.data == "ok", StateFilter(Change_states.awb))
async def book_04(callback: types.CallbackQuery, state: FSMContext):
    await prev[callback.message.chat.id].delete()
    prev[callback.message.chat.id] = await callback.message.answer('Choose an option to change for <b>' + awb[callback.message.chat.id]+'</b>', reply_markup= await get_change_awb(awb[callback.message.chat.id], callback.message.chat.id))
    await state.set_state(Change_states.change)

@router.callback_query(F.data != 'ok', F.data != 'ch', F.data != 'close', F.data != 'go', StateFilter(Change_states.change))
async def book_05(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await prev[callback.message.chat.id].delete()
    #выбрать рейс из инлайн меню если меняется рейс
    dep = await db.get_awb_info('departure', awb=awb[callback.message.chat.id], user_id= callback.message.chat.id)
    dest = await db.get_awb_info('destination', awb=awb[callback.message.chat.id], user_id= callback.message.chat.id)
    date = await db.get_awb_info('date', awb=awb[callback.message.chat.id], user_id= callback.message.chat.id)

    if callback.data == 'flight':
        prev[callback.message.chat.id] = await callback.message.answer(f'Pick a flight from the list below', 
                                                                       reply_markup=await get_flights(departure= dep,
                                                                                                      destination=dest,
                                                                                                      date=date
                                                                                                     )
                                                                        )
        
        print('here')
        await state.set_state(Change_states.flight)
    else:
        prev[callback.message.chat.id] = await callback.message.answer(f'Set new value for <b>{callback.data}</b>')
    change_val[callback.message.chat.id] = callback.data

@router.callback_query(StateFilter(Change_states.flight), F.data != 'prev_pg')
async def book_061(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer(f'<b>{change_val[callback.message.chat.id]}: {callback.data}</b>', reply_markup=confirm_builder.as_markup())
    await db.update_awb(awb[callback.message.chat.id], (change_val[callback.message.chat.id], callback.data))
    await state.set_state(Change_states.change)

@router.callback_query(StateFilter(Change_states.flight), F.data == 'prev_pg')
async def book_062(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await prev[callback.message.chat.id].delete()
    prev[callback.message.chat.id] = await callback.message.answer('Choose an option to change for <b>' + awb[callback.message.chat.id]+'</b>', reply_markup= await get_change_awb(awb[callback.message.chat.id], callback.message.chat.id))
    await state.set_state(Change_states.change)

@router.message(StateFilter(Change_states.change))
async def book_06(message: types.Message, state: FSMContext):
    db = get_db()
    await prev[message.chat.id].delete()
    await message.delete()
    if await is_correct(change_val[message.chat.id], message.text):
        prev[message.chat.id] = await message.answer(f'<b>{change_val[message.chat.id]}: {message.text}</b>', reply_markup=confirm_builder.as_markup())
        await db.update_awb(awb[message.chat.id], (change_val[message.chat.id], message.text))
    else:
        prev[message.chat.id] = await message.answer(f'Incorrect <b>{change_val[message.chat.id]}</b> format')

@router.callback_query(F.data == "ok", StateFilter(Change_states.change))
async def book_07(callback: types.CallbackQuery, state: FSMContext):
    await prev[callback.message.chat.id].delete()
    prev[callback.message.chat.id] = await callback.message.answer('Choose an option to change for <b>' + awb[callback.message.chat.id]+'</b>', reply_markup= await get_change_awb(awb[callback.message.chat.id], callback.message.chat.id))
    await state.set_state(Change_states.change)

@router.callback_query(F.data == "go", StateFilter(Change_states.change))
async def book_08(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    book = Booking()
    await prev[callback.message.chat.id].delete()
    try:
        result = await book.change(awb = awb[callback.message.chat.id], 
                      fr = await db.get_awb_info('departure', awb[callback.message.chat.id], callback.message.chat.id),
                      to = await db.get_awb_info('destination', awb[callback.message.chat.id], callback.message.chat.id),
                      pcs = await db.get_awb_info('pieces', awb[callback.message.chat.id], callback.message.chat.id),
                      w = await db.get_awb_info('weight', awb[callback.message.chat.id], callback.message.chat.id),
                      v = await db.get_awb_info('volume', awb[callback.message.chat.id], callback.message.chat.id),
                      cargo = await db.get_awb_info('cargo', awb[callback.message.chat.id], callback.message.chat.id),
                      flight = await db.get_awb_info('flight', awb[callback.message.chat.id], callback.message.chat.id),
                      day = await db.get_awb_info('date', awb[callback.message.chat.id], callback.message.chat.id),
                      month = await db.get_awb_info('date', awb[callback.message.chat.id], callback.message.chat.id),
                      message = callback.message
                      )
        await callback.message.answer('<code>' + result['ffa'] + '</code>', reply_markup = menu_builder.as_markup())
    except Exception as e:
        await callback.message.answer('something went wrong, please try your request later', reply_markup = menu_builder.as_markup()) 
        print(e)
    await state.set_state(None)


@router.callback_query(F.data == "cn")
async def book_cn(callback: types.CallbackQuery, state: FSMContext):
    prev[callback.message.chat.id] = await callback.message.answer('Choose an option to change for <b>' + awb[callback.message.chat.id]+'</b>', reply_markup= await get_change_awb(awb[callback.message.chat.id], callback.message.chat.id))
    await state.set_state(None)

@router.callback_query(F.data == "close")
async def book_close(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer("Please choose an option in the bottom menu", reply_markup=menu_builder.as_markup())
    await state.set_state(None)

async def is_correct(name, value):
    patterns = {
        'awb': "",
        'pieces': "^\d{1,3}$",
        'weight': "^\d{1,5}\.?\d{1,2}?$",
        'volume': "^\d{1,2}.?\d{1,2}?$",
        'departure': "^\w{3}$",
        'destination': "^\w{3}$",
        'flight': "^\w{2}\d{1,4}$",
        'date': "^\d{2}\w{3}$",
        'cargo': "^.+$"
    }

    if not re.match(patterns[name], value):
        return False
    return True