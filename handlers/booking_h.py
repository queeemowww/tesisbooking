from aiogram import types, Router
from aiogram import F
from utils.isffr import is_ffr, get_info
from utils.book import Booking
from aiogram.types.input_file import FSInputFile
import os
router = Router()

@router.message(F.text)
async def connect_manager(message: types.Message):
    mes = await is_ffr(message.text)
    print(mes)
    if not mes:
        await message.answer("This FFR message is not correct. Please try your request with proper FFR.")
    else:
        awb, fr, to, pcs, w, v, cargo, flight, day, month = await get_info(message.text)
        await message.answer(f"your booking details:\nawb: {awb}\nfrom: {fr}\nto: {to}\npieces: {pcs}\nweight: {w}\nvolume: {v}\ncargo type: {cargo}\nflight number: {flight}\nday: {day}\nmonth: {month}", )
        await message.answer("booking...")
        bk = Booking()
        screenshot = FSInputFile("555-"+awb+".png")
        try:
            await bk.book(awb, fr, to, pcs, w, v, cargo, flight, day, month)
            await message.answer("Success!")
            await message.answer_photo(photo=screenshot)
            os.remove("555-"+awb+".png")
        except Exception as e:
            print(e)
            await message.answer("Something went wrong! Please try your request later")

