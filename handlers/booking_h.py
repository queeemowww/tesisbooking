from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram import F
from aiogram.fsm.context import FSMContext
from utils.isffr import is_ffr, get_info
from utils.book import Booking
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command, StateFilter
from states.booking_states import Bk_states
import os
from kb.booking_kb import confirm_builder, menu_builder, country_builder, get_change_awb, set_client
import re
from database.db_provider import get_db

country = {}
router = Router()

change_val = {}
prev = {}
fr = {}
to = {}
pcs = {}
w = {}
v = {}
day = {}
month = {}
flight = {}
cargo = {}
client = {}

@router.callback_query(F.data == "book", StateFilter(None))
async def book_1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FROM</b> (3 LETTERS, IST, PEK, ICN...)')
    await state.set_state(Bk_states.fr)

@router.message(StateFilter(Bk_states.fr))
async def book_2(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    fr[message.chat.id] = message.text
    if re.match("^\w{3}$", message.text):
        prev[message.chat.id] = await message.answer('FROM: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer("Incorrect departure format")
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.fr))
async def book_3(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FROM</b> (3 LETTERS, IST, PEK, ICN...)')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.fr))
async def book_4(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>TO</b> (3 LETTERS, IST, PEK, ICN...)')
    await state.set_state(Bk_states.to)

@router.message(StateFilter(Bk_states.to))
async def book_5(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    to[message.chat.id] = message.text
    if re.match("^\w{3}$", message.text):
        prev[message.chat.id] = await message.answer('TO: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer("Incorrect destination format")
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.to))
async def book_6(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>TO</b>(3 LETTERS, IST, PEK, ICN...)')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.to))
async def book_7(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>PIECES</b>')
    await state.set_state(Bk_states.pcs)

@router.message(StateFilter(Bk_states.pcs))
async def book_8(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    pcs[message.chat.id] = message.text
    if re.match("^\d{1,3}$", message.text):
        prev[message.chat.id] = await message.answer('PIECES: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect pieces format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.pcs))
async def book_9(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>PIECES</b>')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.pcs))
async def book_10(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>WEIGHT</b>')
    await state.set_state(Bk_states.w)

@router.message(StateFilter(Bk_states.w))
async def book_11(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    w[message.chat.id] = message.text
    if re.match("^\d+\.?\d{1,2}?$", message.text):
        prev[message.chat.id] = await message.answer('WEIGHT: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect weight format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.w))
async def book_12(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>WEIGHT</b>')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.w))
async def book_13(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>VOLUME</b>')
    await state.set_state(Bk_states.v)

@router.message(StateFilter(Bk_states.v))
async def book_14(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    v[message.chat.id] = message.text
    if re.match("^\d{1,4}.?\d{1,2}?$", message.text):
        prev[message.chat.id] = await message.answer('VOLUME: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect volume format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.v))
async def book_15(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>VOLUME</b>')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.v))
async def book_16(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>DAY</b> (2 DIGITS 04, 21, 17...)')
    await state.set_state(Bk_states.day)

@router.message(StateFilter(Bk_states.day))
async def book_17(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    day[message.chat.id] = message.text
    if re.match("^\d{1,2}$", message.text):
        prev[message.chat.id] = await message.answer('DAY: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect day format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.day))
async def book_18(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>DAY</b> (2 DIGITS 04, 21, 17...)')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.day))
async def book_19(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>MONTH</b> (3 CHARACTERS MAR, OCT, FEB...)')
    await state.set_state(Bk_states.month)

@router.message(StateFilter(Bk_states.month))
async def book_20(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    month[message.chat.id] = message.text
    if re.match("^\w{3}$", message.text):
        prev[message.chat.id] = await message.answer('MONTH: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('Incorrect month format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.month))
async def book_21(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>MONTH</b> (3 CHARACTERS MAR, OCT, FEB...)')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.month))
async def book_22(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FLIGHT</b> (SU2139, FV6532, HZ3232...)')
    await state.set_state(Bk_states.flight)

@router.message(StateFilter(Bk_states.flight))
async def book_23(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    flight[message.chat.id] = message.text
    if re.match('^\w{2}\d{1,4}$', message.text):
        prev[message.chat.id] = await message.answer('FLIGHT: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        prev[message.chat.id] = await message.answer('incorrect flight format')
        await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.flight))
async def book_24(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>FLIGHT</b> (SU2139, FV6532, HZ3232...)')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.flight))
async def book_25(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>CARGO TYPE</b>(SPP, EQUIPMENT...)')
    await state.set_state(Bk_states.client)

@router.message(StateFilter(Bk_states.client))
async def book_26(message: types.Message, state: FSMContext):
    await prev[message.chat.id].delete()
    del prev[message.chat.id]
    cargo[message.chat.id] = message.text
    await message.answer('CARGO: <b> ' + message.text+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
    await message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.client))
async def book_27(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>CARGO TYPE</b>(SPP, EQUIPMENT...)')

@router.callback_query(F.data == "ok", StateFilter(Bk_states.client))
async def book_251(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>CLIENT</b>(Limittrans, routas)', reply_markup= await set_client())
    await state.set_state(Bk_states.cargo)

@router.callback_query(StateFilter(Bk_states.cargo), F.data != 'ok', F.data != 'cancel', F.data != "close", F.data != 'ch', F.data != 'cn')
async def book_246(callback: types.CallbackQuery, state: FSMContext):
    try:
        await prev[callback.message.chat.id].delete()
        del prev[callback.message.chat.id]
    except:
        pass
    client[callback.message.chat.id] = callback.data
    await callback.message.answer('Client: <b> ' + callback.data+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)

@router.callback_query(F.data == "ch", StateFilter(Bk_states.cargo))
async def book_527(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>CLIENT</b>(Limittrans, routas)', reply_markup= await set_client())

@router.callback_query(F.data == "ok", StateFilter(Bk_states.cargo))
async def book_27_01(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await db.insert_awb(awb=f'ID{callback.message.chat.id}',
                            pieces=pcs[callback.message.chat.id],
                            weight=w[callback.message.chat.id],
                            volume=v[callback.message.chat.id],
                            cargo=cargo[callback.message.chat.id],
                            departure=fr[callback.message.chat.id],
                            destination=to[callback.message.chat.id],
                            flight=flight[callback.message.chat.id],
                            date=day[callback.message.chat.id]+month[callback.message.chat.id],
                            booking_status='ND',
                            arrival_status='ND',
                            client=client[callback.message.chat.id],
                            user_id=callback.message.chat.id)
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('Here is your reservation. You can edit it or proceed ', reply_markup= await get_change_awb(f'ID{callback.message.chat.id}', callback.message.chat.id))
    await state.set_state(Bk_states.final)

@router.callback_query(StateFilter(Bk_states.final), F.data != 'cn', F.data != 'ok', F.data != 'go', F.data != 'go', F.data != 'close')
async def book_02336(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await prev[callback.message.chat.id].delete()
    prev[callback.message.chat.id] = await callback.message.answer(f"<b>Set new value for {callback.data}</b>")
    change_val[callback.message.chat.id] = callback.data


@router.message(StateFilter(Bk_states.final))
async def book_0236(message: types.Message, state: FSMContext):
    db = get_db()
    await prev[message.chat.id].delete()
    await message.delete()
    if await is_correct(change_val[message.chat.id], message.text):
        prev[message.chat.id] = await message.answer(f'<b>{change_val[message.chat.id]}: {message.text}</b>', reply_markup=confirm_builder.as_markup())
        await db.update_awb(f'ID{message.chat.id}', (change_val[message.chat.id], message.text))
    else:
        prev[message.chat.id] = await message.answer(f'Incorrect <b>{change_val[message.chat.id]}</b> format')

@router.callback_query(StateFilter(Bk_states.final), F.data == 'ok')
async def book_136(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('Here is your reservation. You can edit it or proceed ', reply_markup= await get_change_awb(f'ID{callback.message.chat.id}', callback.message.chat.id))

@router.callback_query(StateFilter(Bk_states.final), F.data == 'ch')
async def book_113123(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await prev[callback.message.chat.id].delete()
    prev[callback.message.chat.id] = await callback.message.answer(f"<b>Set new value for {callback.data}</b>")
    change_val[callback.message.chat.id] = callback.data

@router.callback_query(F.data == "go", StateFilter(Bk_states.final))
async def book_27_1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>SELECT A COUNTRY</b>', reply_markup=country_builder.as_markup())
    await state.set_state(Bk_states.country)


# @router.callback_query(StateFilter(Bk_states.country))
# async def book_27_2(callback: types.CallbackQuery, state: FSMContext):
#     await prev[callback.message.chat.id].delete()
#     del prev[callback.message.chat.id]
#     country[callback.message.chat.id] = callback.data
#     await callback.message.answer('COUNTRY: <b> ' + callback.data+ "</b>", reply_markup=confirm_builder.as_markup(), parse_mode=ParseMode.HTML)
#     await callback.message.delete()

@router.callback_query(F.data == "ch", StateFilter(Bk_states.country))
async def book_27_3(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('<b>SELECT A COUNTRY</b>', reply_markup=country_builder.as_markup())

# @router.callback_query(F.data == "CHINA", StateFilter(Bk_states.country))
# async def book_28(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.delete()
#     bk = Booking(country="CHINA")
#     try:
#         result = await bk.book(fr=fr[callback.message.chat.id], to = to[callback.message.chat.id], pcs=pcs[callback.message.chat.id], w=w[callback.message.chat.id], v=v[callback.message.chat.id], day=day[callback.message.chat.id], month=month[callback.message.chat.id], flight=flight[callback.message.chat.id], cargo=cargo[callback.message.chat.id], message=callback.message)
#         await callback.message.answer(result['ffa'], reply_markup = menu_builder.as_markup())
#     except Exception as e:
#         await callback.message.answer("Something went wrong, plaese try your request later")
#     await state.set_state(None)

@router.callback_query(F.data == "TURKEY", StateFilter(Bk_states.country))
async def book_28_1(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    bk = Booking(country="TURKEY")
    db = get_db()
    # try:
    result = await bk.book(fr=fr[callback.message.chat.id], to = to[callback.message.chat.id], pcs=pcs[callback.message.chat.id], w=w[callback.message.chat.id], v=v[callback.message.chat.id], day=day[callback.message.chat.id], month=month[callback.message.chat.id], flight=flight[callback.message.chat.id], cargo=cargo[callback.message.chat.id], message=callback.message)
    await db.update_awb(f'ID{callback.message.chat.id}', ('awb', result['awb']))
    await callback.message.answer('<code>' + result['ffa'] + '</code>', reply_markup = menu_builder.as_markup())

    # except Exception as e:
        # await callback.message.answer("Something went wrong, plaese try your request later")
    await state.set_state(None)

@router.callback_query(F.data == "cn", F.data == 'close')
async def book_cn(callback: types.CallbackQuery, state: FSMContext):
    db = get_db()
    await db.delete_awb(f"{callback.message.chat.id}")
    await callback.message.delete()
    prev[callback.message.chat.id] = await callback.message.answer('cancelled', reply_markup=menu_builder.as_markup())
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
        'cargo': "^.+$",
        'client': ".+\s+"
    }

    if not re.match(patterns[name], value):
        return False
    return True
