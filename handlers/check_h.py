from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram import F
from aiogram.fsm.context import FSMContext
from utils.isffr import is_ffr, get_info
from utils.book import Booking
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command, StateFilter
from states.booking_states import Check_states
import os
from kb.booking_kb import confirm_builder, menu_builder,country_builder
from database.db_provider import get_db

import re
router = Router()
prev = {}
awb = {}
country = {}

awb_pattern = "^555-\d{8}$"

@router.callback_query(F.data == "check", StateFilter(None))
async def book_01(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>AWB</b> 11 digits separated with -')
    await state.set_state(Check_states.check)

@router.message(StateFilter(Check_states.check))
async def book_02(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    awb[message.chat.id] = message.text
    if re.match(awb_pattern, message.text):
        await message.answer('AWB: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect awb format')
        await message.delete()
@router.callback_query(F.data == "ch", StateFilter(Check_states.check))
async def book_03(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>AWB</b> 11 digits separated with -)')

@router.callback_query(F.data == "ok", StateFilter(Check_states.check))
async def book_27_1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('<b>SELECT A COUNTRY</b>', reply_markup=country_builder.as_markup())
    await state.set_state(Check_states.country)

@router.callback_query(F.data == "ch", StateFilter(Check_states.country))
async def book_27_3(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>SELECT A COUNTRY</b>', reply_markup=country_builder.as_markup())

@router.callback_query(F.data == "CHINA", StateFilter(Check_states.country))
async def book_04(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await callback.message.delete()
    bk = Booking(country='CHINA')
    try:
        status = await bk.check(awb=awb[callback.message.chat.id], message=callback.message)
        await callback.message.answer(f"{awb[callback.message.chat.id]}: {status}", reply_markup = menu_builder.as_markup())
        await db.update_awb(awb=awb[callback.message.chat.id], upd_val=('booking_status', status))
    except Exception as e:
        await callback.message.answer("Something went wrong, plaese try your reqest later")
    await state.set_state(None)

@router.callback_query(F.data == "TURKEY", StateFilter(Check_states.country))
async def book_05(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await callback.message.delete()
    bk = Booking(country='TURKEY')
    try:
        status = await bk.check(awb=awb[callback.message.chat.id], message=callback.message)
        await callback.message.answer(f"{awb[callback.message.chat.id]}: {status}", reply_markup = menu_builder.as_markup())
        await db.update_awb(awb=awb[callback.message.chat.id], upd_val=('booking_status', status))
    except Exception as e:
        await callback.message.answer("Something went wrong, plaese try your reqest later")
    await state.set_state(None)

@router.callback_query(F.data == "cn")
async def book_cn(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('cancelled', reply_markup=menu_builder.as_markup())
    await state.set_state(None)