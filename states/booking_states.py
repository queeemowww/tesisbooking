from aiogram.filters.state import State, StatesGroup 

class Bk_states(StatesGroup):
    fr = State()
    to = State()
    pcs = State()
    w = State()
    v = State()
    day = State()
    month = State()
    flight = State()
    cargo = State()
    client = State()
    client_choose = State()
    final = State()
    country = State()

class Change_states(StatesGroup):
    awb = State()
    change = State()
    flight = State()
    
class Cancel_states(StatesGroup):
    cancel = State()
    country = State()

class Check_states(StatesGroup):
    check = State()
    country = State()

class Awb_states(StatesGroup):
    awb = State()