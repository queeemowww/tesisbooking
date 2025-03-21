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
from kb.booking_kb import confirm_builder, menu_builder

import re
router = Router()
prev = {}
awb = {}

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
    if re.match("555-\d{8}", message.text):
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
async def book_04(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    bk = Booking()
    await bk.check(awb=awb[callback.message.chat.id], message=callback.message)
    await state.set_state(None)

@router.callback_query(F.data == "cn")
async def book_cn(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('cancelled', reply_markup=menu_builder.as_markup())
    await state.set_state(None)