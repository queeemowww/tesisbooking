from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

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

