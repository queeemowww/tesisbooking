from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram import F
from aiogram.fsm.context import FSMContext
from utils.isffr import is_ffr, get_info
from utils.book import Booking
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command, StateFilter
from states.booking_states import Awb_states
import os
from kb.booking_kb import confirm_builder, menu_builder, country_builder, get_awb_history, get_info
import re

router = Router()
pg = {}
prev = {}


@router.callback_query(F.data == "history", StateFilter(None))
async def book_1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    pg[callback.message.chat.id] = 0
    prev[callback.message.chat.id] = await callback.message.answer('My Airwaybills📑', reply_markup=await get_awb_history(callback.message.chat.id, pg=pg[callback.message.chat.id]))
    await state.set_state(Awb_states.awb)

@router.callback_query(F.data == "next_pg", StateFilter(Awb_states.awb))
async def book_2(callback: types.CallbackQuery, state: FSMContext):
    pg[callback.message.chat.id] += 1
    await prev[callback.message.chat.id].edit_reply_markup(reply_markup=await get_awb_history(callback.message.chat.id, pg=pg[callback.message.chat.id]))

@router.callback_query(F.data == "prev_pg", StateFilter(Awb_states.awb))
async def book_3(callback: types.CallbackQuery, state: FSMContext):
    pg[callback.message.chat.id] -= 1
    if pg[callback.message.chat.id] < 0:
        pg[callback.message.chat.id] = 0
    try:
        await prev[callback.message.chat.id].edit_text('My Airwaybills📑', reply_markup= await get_awb_history(callback.message.chat.id, pg=pg[callback.message.chat.id]))
    except Exception as e:
        print(e)
        pass

@router.callback_query(F.data != 'close', StateFilter(Awb_states.awb))
async def book_4(callback: types.CallbackQuery, state: FSMContext):
    pg[callback.message.chat.id] += 1
    await prev[callback.message.chat.id].edit_text("<code>"+callback.data+'📄</code>', reply_markup= await get_info(callback.data, callback.message.chat.id))


@router.callback_query(F.data == 'close', StateFilter(Awb_states.awb))
async def book_5(callback: types.CallbackQuery, state: FSMContext):
    del pg[callback.message.chat.id]
    await prev[callback.message.chat.id].edit_text("Please choose an option", reply_markup=menu_builder.as_markup())
    await state.set_state(None)

