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
from kb.booking_kb import confirm_builder, menu_builder
import re

router = Router()
prev = {}
awb = {}
fr = {}
to = {}
pcs = {}
w = {}
v = {}
day = {}
month = {}
flight = {}
cargo = {}

awb_pattern = "555-\d{8}"

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
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>AWB</b> 11 digits separated with -)')

@router.callback_query(F.data == "ok", StateFilter(Change_states.awb))
async def book_04(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FROM</b> (3 LETTERS, IST, PEK, ICN...)')
    await state.set_state(Change_states.fr)

@router.message(StateFilter(Change_states.fr))
async def book_2(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    fr[message.chat.id] = message.text
    if re.match("\w{3}", message.text):
        prev[message.chat.id] = await message.answer('FROM: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer("Incorrect departure format")
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.fr))
async def book_3(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FROM</b> (3 LETTERS, IST, PEK, ICN...)')

@router.callback_query(F.data == "ok", StateFilter(Change_states.fr))
async def book_4(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>TO</b> (3 LETTERS, IST, PEK, ICN...)')
    await state.set_state(Change_states.to)

@router.message(StateFilter(Change_states.to))
async def book_5(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    to[message.chat.id] = message.text
    if re.match("\w{3}", message.text):
        prev[message.chat.id] = await message.answer('TO: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer("Incorrect destination format")
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.to))
async def book_6(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>TO</b>(3 LETTERS, IST, PEK, ICN...)')

@router.callback_query(F.data == "ok", StateFilter(Change_states.to))
async def book_7(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>PIECES</b>')
    await state.set_state(Change_states.pcs)

@router.message(StateFilter(Change_states.pcs))
async def book_8(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    pcs[message.chat.id] = message.text
    if re.match("\d{1,3}", message.text):
        prev[message.chat.id] = await message.answer('PIECES: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect pieces format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.pcs))
async def book_9(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>PIECES</b>')

@router.callback_query(F.data == "ok", StateFilter(Change_states.pcs))
async def book_10(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>WEIGHT</b>')
    await state.set_state(Change_states.w)

@router.message(StateFilter(Change_states.w))
async def book_11(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    w[message.chat.id] = message.text
    if re.match("\d+\.?\d{1,2}?", message.text):
        prev[message.chat.id] = await message.answer('WEIGHT: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect weight format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.w))
async def book_12(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>WEIGHT</b>')

@router.callback_query(F.data == "ok", StateFilter(Change_states.w))
async def book_13(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>VOLUME</b>')
    await state.set_state(Change_states.v)

@router.message(StateFilter(Change_states.v))
async def book_14(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    v[message.chat.id] = message.text
    if re.match("\d+\.?\d{1,2}?", message.text):
        prev[message.chat.id] = await message.answer('VOLUME: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect volume format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.v))
async def book_15(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>VOLUME</b>')

@router.callback_query(F.data == "ok", StateFilter(Change_states.v))
async def book_16(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>DAY</b> (2 DIGITS 04, 21, 17...)')
    await state.set_state(Change_states.day)

@router.message(StateFilter(Change_states.day))
async def book_17(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    day[message.chat.id] = message.text
    if re.match("\d{1,2}", message.text):
        prev[message.chat.id] = await message.answer('DAY: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect day format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.day))
async def book_18(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>DAY</b> (2 DIGITS 04, 21, 17...)')

@router.callback_query(F.data == "ok", StateFilter(Change_states.day))
async def book_19(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>MONTH</b> (3 CHARACTERS MAR, OCT, FEB...)')
    await state.set_state(Change_states.month)

@router.message(StateFilter(Change_states.month))
async def book_20(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    month[message.chat.id] = message.text
    if re.match("\w{3}", message.text):
        prev[message.chat.id] = await message.answer('MONTH: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect month format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.month))
async def book_21(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>MONTH</b> (3 CHARACTERS MAR, OCT, FEB...)')

@router.callback_query(F.data == "ok", StateFilter(Change_states.month))
async def book_22(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FLIGHT</b> (SU2139, FV6532, HZ3232...)')
    await state.set_state(Change_states.flight)

@router.message(StateFilter(Change_states.flight))
async def book_23(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    flight[message.chat.id] = message.text
    if re.match('\w{2}\d{1,4}', message.text):
        prev[message.chat.id] = await message.answer('FLIGHT: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('incorrect flight format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.flight))
async def book_24(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FLIGHT</b> (SU2139, FV6532, HZ3232...)')

@router.callback_query(F.data == "ok", StateFilter(Change_states.flight))
async def book_25(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>CARGO TYPE</b>(SPP, EQUIPMENT...)')
    await state.set_state(Change_states.cargo)

@router.message(StateFilter(Change_states.cargo))
async def book_26(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    cargo[message.chat.id] = message.text
    await message.answer('CARGO: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
    await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Change_states.cargo))
async def book_27(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FLIGHT</b> (SU2139, FV6532, HZ3232...)')

@router.callback_query(F.data == "ok", StateFilter(Change_states.cargo))
async def book_28(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    bk = Booking()
    await bk.change(awb=awb[callback.message.chat.id],fr=fr[callback.message.chat.id], to = to[callback.message.chat.id], pcs=pcs[callback.message.chat.id], w=w[callback.message.chat.id], v=v[callback.message.chat.id], day=day[callback.message.chat.id], month=month[callback.message.chat.id], flight=flight[callback.message.chat.id], cargo=cargo[callback.message.chat.id], message=callback.message)
    await state.set_state(None)

@router.callback_query(F.data == "cn")
async def book_cn(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('cancelled', reply_markup=menu_builder.as_markup())
    await state.set_state(None)
