from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import os
import asyncio
from dotenv import load_dotenv
import time
from db import Db
load_dotenv()

database = Db()
prev = {}

ADMIN_ID = os.getenv('ADMIN_ID')
LOGIN_TR = os.getenv('LOGIN_TR')
PASS_TR = os.getenv('PASS_TR')

LOGIN_CN = os.getenv('LOGIN_CN')
PASS_CN = os.getenv('PASS_CN')

class Booking():
    def __init__(self, country = "TURKEY"):
        if country == "TURKEY":
            self.login = LOGIN_TR
            self.password = PASS_TR
        if country == "CHINA":
            self.login = LOGIN_CN
            self.password = PASS_CN

        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(self.chrome_options)

    async def book(self, awb = None, fr = None, to = None, pcs = None, w = None, v = None, cargo = None, flight = None, day = None, month = None, message = None):
        url = 'https://afl.booking-cargo.ru/'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        prev[message.chat.id] = await message.answer(f"Authorizing: ⏳{round(1/20*100, 2)}%⏳")
        while True:
            try:
                login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
                pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
                break
            except:
                pass
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)

        while True:
            try:
                book_el1 = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-col ant-col-4 css-lked6w"]')
                book_el1.click()
                break
            except:
                pass
        await prev[message.chat.id].edit_text(f"Filling up boking details: ⏳{round(6/20*100, 2)}%⏳")

        while True:
            try:
                awb_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[5]
                awb_input_el.send_keys(Keys.ENTER, Keys.ENTER)
                break
            except:
                pass
        awb_actual = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-select-selector"]')[3].text
        while True:
            try:
                from_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[8]
                from_input_el.send_keys(fr, Keys.ENTER)
                to_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[9]
                to_input_el.send_keys(to, Keys.ENTER)
                pcs_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[11]
                pcs_input_el.send_keys(pcs, Keys.ENTER)
                weight_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[13]
                weight_input_el.send_keys(w, Keys.ENTER)
                vol_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[15]
                vol_input_el.send_keys(v, Keys.ENTER)
                cargo_input_el = self.browser.find_elements(By.TAG_NAME, 'textarea')[0]
                cargo_input_el.send_keys(cargo, Keys.ENTER)
                break
            except:
                pass
        while True:
            try:
                choose_flight_el = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm FormFlightBuilder__ButtonPickFlights-hFgekQ SOGsx"]')
                choose_flight_el.click()
                break
            except:
                pass

        next_pg_elem = self.browser.find_element(By.CSS_SELECTOR, '[class = "anticon anticon-right"]')
        flag = True
        await prev[message.chat.id].edit_text(f"Confirming: ⏳{round(12/20*100, 2)}%⏳")
        while (flag):
            flight_elems = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
            for flight_info in flight_elems:
                td_elems = flight_info.find_elements(By.TAG_NAME, "td")
                flightnum_elem = td_elems[3]
                if flightnum_elem.text.lower() == flight.lower() and td_elems[2].text[:2] == day:
                    td_elems[0].click()
                    flag = False
                    break
            try:
                next_pg_elem.click()
                time.sleep(1)
            except:
                continue
        while True:
            try:
                apply_el = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-sm"]')
                apply_el.click()
                break
            except:
                pass
        confirm_el = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-primary ant-btn-color-primary ant-btn-variant-solid"]')[1]
        confirm_el.click()
        await prev[message.chat.id].edit_text("Your awb number is: " + awb_actual)
        while True:
            try:
                flight_actual = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm ButtonLink__ButtonStyled-eeryZM gvPyWL"]').text
                booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
                break
            except:
                pass
        ffa = f"""FFA/4
{awb_actual}{fr}{to}/T{pcs}K{w}MC{v}/{cargo}
{flight_actual}/{day}{month}/{fr}{to}/{booking_status}
REF/CHACSSU""".upper()
        await prev[message.chat.id].edit_text('<code>' + ffa + '</code>')
        database.insert_awb(awb_actual, flight_actual, day+month.upper(), booking_status, 'NO DATA', message.chat.id)
        await message.bot.send_message(chat_id=ADMIN_ID, text = f'{message.chat.full_name}:<code>{ffa}</code>')
        del prev[message.chat.id]
        self.browser.close()

    async def change(self, awb, fr = None, to = None, pcs = None, w = None, v = None, cargo = None, flight = None, day = None, month = None, message = None):
        url = 'https://afl.booking-cargo.ru/waybills'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        prev[message.chat.id] = await message.answer(f"Authorizing: ⏳{round(1/34*100, 2)}%⏳")
        while True:
            try:
                login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
                pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
                break
            except:
                pass
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)
        while True:
            try:
                self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-picker-clear"]').click()
                break
            except:
                pass
        await prev[message.chat.id].edit_text(f"Authorizing: ⏳{round(4/34*100, 2)}%⏳")
        while True:
            try:
                booked_flights_els = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
                if len(booked_flights_els) > 0:
                    break
            except:
                pass
        for i in range(len(booked_flights_els)):
            booked_flight = booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].text
            if booked_flight == awb:
                booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].click()
                break
        #старый букинг
        while True:
            try:
                booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
                break
            except:
                pass
        await prev[message.chat.id].edit_text(f"Previous booking status:  " + '<b>' +  booking_status + '</b>' +f"⏳{round(15/34*100, 2)}%⏳")
        while True:
            try:
                self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-circle ant-btn-text ant-btn-color-default ant-btn-variant-text ant-btn-sm ant-btn-icon-only"]')[2].click()
                break
            except:
                pass
        while True:
            try:
                new_booking_els = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]').find_elements(By.TAG_NAME, "input")
                break
            except:
                pass
        new_booking_els[0].send_keys(Keys.COMMAND+"a")
        time.sleep(.5)
        new_booking_els[0].send_keys(Keys.DELETE)
        time.sleep(.2)
        new_booking_els[0].send_keys(pcs)

        new_booking_els[1].send_keys(Keys.COMMAND+"a")
        time.sleep(.5)
        new_booking_els[1].send_keys(Keys.DELETE)
        time.sleep(.2)
        new_booking_els[1].send_keys(w)
        await prev[message.chat.id].edit_text(f"Previous booking status:  " + '<b>' +  booking_status + '</b>' +f"⏳{round(20/34*100, 2)}%⏳")
        new_booking_els[2].send_keys(Keys.COMMAND+"a")
        time.sleep(.5)
        new_booking_els[2].send_keys(Keys.DELETE)
        time.sleep(.2)
        new_booking_els[2].send_keys(v)

        while True:
            try:
                self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]').find_element(By.TAG_NAME, "button").click()
                break
            except:
                pass
        #новый букинг
        while True:
            try:
                booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
                break
            except:
                pass
        while True:
            try:
                self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-circle ant-btn-text ant-btn-color-default ant-btn-variant-text ant-btn-sm ant-btn-icon-only"]')[3].click()
                if len(self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-circle ant-btn-text ant-btn-color-default ant-btn-variant-text ant-btn-sm ant-btn-icon-only"]'))> 0:
                    break
            except:
                pass
        while True:
            try:
                self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")[2].click()
                if len(self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")) > 0:
                    break
            except:
                pass
        await prev[message.chat.id].edit_text(f"Searching for new flight: ⏳{round(26/34*100, 2)}%⏳")
        flag = True
        i =0
        while(flag):
            i += 1
            time.sleep(1)
            while True:
                try:
                    flights_els = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-table-wrapper TableBookingFlight__TableStyled-gHCKPF ksiLWd css-lked6w"]').find_elements(By.TAG_NAME, "tr")
                    if len(flights_els) > 0:
                        break
                except:
                    pass
            for i in range(2, len(flights_els)):
                if flights_els[i].find_elements(By.TAG_NAME, "td")[2].text[:2] == day and flights_els[i].find_elements(By.TAG_NAME, "td")[3].text.lower() == flight.lower():
                    flights_els[i].find_elements(By.TAG_NAME, "td")[0].click()
                    flag = False
                    break
            try:
                self.browser.find_elements(By.CSS_SELECTOR, '[title = "Вперед"]')[0].click()
            except:
                pass
            await prev[message.chat.id].edit_text(f"Searching for new flight: ⏳{round((29+i)/34*100, 2)}%⏳")
        while True:
            try:
                self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")[0].click()
                if len(self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")) > 0:
                    break
            except:
                pass
        while True:
            try:
                self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")[3].click()
                if len(self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')[0].find_elements(By.TAG_NAME, "button")) > 0:
                    break
            except:
                pass
        booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
        await prev[message.chat.id].edit_text(f"New booking status  " + '<b>' +  booking_status + f'</b>: ⏳{round(33/34*100, 2)}%⏳')
        awb_actual = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-select-selector"]')[3].text
        while True:
            try:
                flight_actual = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm ButtonLink__ButtonStyled-eeryZM gvPyWL"]').text
                break
            except:
                pass
        ffa = f"""FFA/4
{awb}{fr}{to}/T{pcs}K{w}MC{v}/{cargo}
{flight_actual}/{day}{month}/{fr}{to}/{booking_status}
REF/CHACSSU""".upper()
        await prev[message.chat.id].edit_text('<code>' + ffa + '</code>')
        database.update_awb(awb, ['booking_status', booking_status])
        database.update_awb(awb, ['flight', flight_actual])
        database.update_awb(awb, ['date', day+month.upper()])
        await message.bot.send_message(chat_id=ADMIN_ID, text = f'{message.chat.full_name}:<code>{ffa}</code>')
        del prev[message.chat.id]
        self.browser.close()

    async def cancel(self, awb, message):
        url = 'https://afl.booking-cargo.ru/waybills'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        prev[message.chat.id] = await message.answer(f"Authorizing% ⏳{round(1/34*100, 2)}%⏳")
        while True:
            try:
                login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
                pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
                break
            except:
                pass
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)
        while True:
            try:
                self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-picker-clear"]').click()
                break
            except:
                pass
        while True:
            try:
                booked_flights_els = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
                if len(booked_flights_els) > 0:
                    break
            except:
                pass
        await prev[message.chat.id].edit_text(f"Searching for {awb}: ⏳{round(10/34*100, 2)}%⏳")
        for i in range(len(booked_flights_els)):
            booked_flight = booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].text
            if booked_flight == awb:
                booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].click()
                await prev[message.chat.id].edit_text(f"Found {awb}: ⏳{round(21/34*100, 2)}%⏳")
                break
        while True:
            try:
                booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
                break
            except:
                pass
        if booking_status != "KK":
            await prev[message.chat.id].edit_text(f"{awb}:  " + '<b>' +  booking_status + '</b>')
            return

        while True:
            try:
                self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-default ant-btn-dangerous ant-btn-color-dangerous ant-btn-variant-outlined ant-btn-sm"]').click()
                break
            except:
                pass
        time.sleep(1)
        while True:
            try:
                booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
                break
            except:
                pass
        database.update_awb(awb, ['booking_status', booking_status])
        await prev[message.chat.id].edit_text(f"{awb}:  " + '<b>' +  booking_status + '</b>')
        self.browser.close()

    async def check(self, awb, message = None, auto = None):
        url = 'https://afl.booking-cargo.ru/waybills'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        if not auto:
            prev[message.chat.id] = await message.answer(f"Authorizing: ⏳{round(1/34*100, 2)}%⏳")
        while True:
            try:
                login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
                pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
                break
            except:
                pass
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)
        await prev[message.chat.id].edit_text(f"Authorizing: ⏳{round(10/34*100, 2)}%⏳")
        while True:
            try:
                self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-picker-clear"]').click()
                break
            except:
                pass
        while True:
            try:
                booked_flights_els = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
                if len(booked_flights_els) > 0:
                    break
            except:
                pass
        while True:
            try:
                for i in range(len(booked_flights_els)):
                    booked_flight = booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].text
                    print(booked_flight)
                    if booked_flight == awb:
                        print('HERE')
                        booked_flights_els[i].find_elements(By.TAG_NAME, "td")[2].click()
                        break
                print('click')
                break
            except:
                pass
        while True:
            try:
        #старый букинг
                booking_status = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-tabs-tabpane ant-tabs-tabpane-active"]')[4].find_elements(By.CSS_SELECTOR, '[class = "ant-col css-lked6w"]')[2].find_elements(By.CSS_SELECTOR, '[class = "ant-descriptions-item-content"]')[0].text
                break
            except:
                pass
        database.update_awb(awb, ['booking_status', booking_status])
        if not auto:
            await prev[message.chat.id].edit_text(f"{awb}:  " + '<b>' +  booking_status + '</b>')
            await message.answer(f"{awb}:  " + '<b>' +  booking_status + '</b>')
        return booking_status

    async def available_flghts(self, fr, to, day, month, message = None, aircrafts = ['73H', '77W']):
        possible_flights = []
        url = 'https://afl.booking-cargo.ru/'
        if requests.get(url).status_code != 200:
            return 'The service is not available at the moment. Please try your request later'
        self.browser.get(url)
        # prev[message.chat.id] = await message.answer(f"Authorizing: ⏳{round(1/20*100, 2)}%⏳")
        while True:
            try:
                if len(self.browser.find_elements(By.TAG_NAME, "input")) > 0:
                    login_el = self.browser.find_elements(By.TAG_NAME, "input")[0]
                    pass_el = self.browser.find_elements(By.TAG_NAME, "input")[1]
                    break
            except:
                pass
        login_el.send_keys(self.login)
        pass_el.send_keys(self.password, Keys.ENTER)
        while True:
            try:
                if len(self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-col ant-col-4 css-lked6w"]')) > 0:
                    book_el1 = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-col ant-col-4 css-lked6w"]')
                    book_el1.click()
                    break
            except:
                pass
        while True:
            try:
                if len(self.browser.find_elements(By.TAG_NAME, 'input')) > 0:
                    awb_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[5]
                    awb_input_el.send_keys(Keys.ENTER)
                    time.sleep(.1)
                    awb_input_el.send_keys(Keys.ENTER)
                    break
            except:
                pass
        
        while True:
            try:
                from_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[8]
                from_input_el.send_keys(fr, Keys.ENTER)
                to_input_el = self.browser.find_elements(By.TAG_NAME, 'input')[9]
                to_input_el.send_keys(to, Keys.ENTER)
                break
            except:
                pass

        while True:
            try:
                if len(self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm FormFlightBuilder__ButtonPickFlights-hFgekQ SOGsx"]')) > 0:
                    choose_flight_el = self.browser.find_element(By.CSS_SELECTOR, '[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm FormFlightBuilder__ButtonPickFlights-hFgekQ SOGsx"]')
                    choose_flight_el.click()
                    break
            except:
                pass
        while True:
            try:
                if len(self.browser.find_elements(By.CSS_SELECTOR, '[class = "anticon anticon-right"]')) > 0:
                    next_pg_elem = self.browser.find_element(By.CSS_SELECTOR, '[class = "anticon anticon-right"]')
                    break
            except:
                pass
        flag = True
        # await prev[message.chat.id].edit_text(f"Confirming: ⏳{round(12/20*100, 2)}%⏳")
        while (flag):
            while True:
                try:
                    if len(self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')) > 0:
                        flight_elems = self.browser.find_elements(By.CSS_SELECTOR, '[class = "ant-table-row ant-table-row-level-0"]')
                        break
                except:
                    pass
            for flight_info in flight_elems:
                td_elems = flight_info.find_elements(By.TAG_NAME, "td")
                flightnum_elem = td_elems[3]
                availability = td_elems[-1]
                date_el = td_elems[2]
                aircraft_el = td_elems[8]
                if date_el.text[:2] >= day and availability.text != 'Занято' and (aircraft_el.text in aircrafts):
                    possible_flights.append((flightnum_elem.text, availability.text, date_el.text[:2]+month.upper()))
                    if int(date_el.text[:2]) > int(day):
                        flag = False
                        break
            try:
                next_pg_elem.click()
                time.sleep(1)
            except:
                continue
        self.browser.close()
        return possible_flights

# if __name__ == '__main__':
#     bk = Booking("TURKEY")
#     print(asyncio.run(bk.available_flghts('ist', 'svo', '29', 'mar')))