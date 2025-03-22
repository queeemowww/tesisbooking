from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram import F
from aiogram.fsm.context import FSMContext
from utils.isffr import is_ffr, get_info
from utils.book import Booking
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command, StateFilter
from states.booking_states import Cancel_states
import os
from kb.booking_kb import confirm_builder, menu_builder, country_builder
router = Router()
country = {}

prev = {}
awb = {}

@router.callback_query(F.data == "cancel", StateFilter(None))
async def book_01(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>AWB</b> 11 digits separated with -')
    await state.set_state(Cancel_states.cancel)

@router.message(StateFilter(Cancel_states.cancel))
async def book_02(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    awb[message.chat.id] = message.text
    await message.answer('AWB: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
    await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Cancel_states.cancel))
async def book_03(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>AWB</b> 11 digits separated with -)')

@router.callback_query(F.data == "ok", StateFilter(Cancel_states.cancel))
async def book_27_1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>SELECT A COUNTRY</b>', reply_markup=country_builder.as_markup())
    await state.set_state(Cancel_states.country)

# @router.callback_query(StateFilter(Cancel_states.country))
# async def book_27_2(callback: types.CallbackQuery, state: FSMContext):
#     await prev[callback.message.chat.id].delete()
#     del prev[callback.message.chat.id]
#     country[callback.message.chat.id] = callback.data
#     await callback.message.answer('COUNTRY: <b> ' + callback.data+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
#     await callback.message.delete()

@router.callback_query(F.data == "ch", StateFilter(Cancel_states.country))
async def book_27_3(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>SELECT A COUNTRY</b>', reply_markup=country_builder.as_markup())

@router.callback_query(F.data == "CHINA", StateFilter(Cancel_states.country))
async def book_04(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    bk = Booking(country='CHINA')
    try:
        await bk.cancel(awb=awb[callback.message.chat.id], message=callback.message)
    except Exception as e:
        await callback.message.answer(str(e))
    await state.set_state(None)

@router.callback_query(F.data == "TURKEY", StateFilter(Cancel_states.country))
async def book_05(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    bk = Booking(country='TURKEY')
    try:
        await bk.cancel(awb=awb[callback.message.chat.id], message=callback.message)
    except Exception as e:
        await callback.message.answer(str(e))
    await state.set_state(None)

@router.callback_query(F.data == "cn")
async def book_cn(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('cancelled', reply_markup=menu_builder.as_markup())
    await state.set_state(None)