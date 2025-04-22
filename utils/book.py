import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from database.db_provider import get_db
import time
import re

prev = {}  # если prev – глобальный словарь
load_dotenv()

LOGIN_TR = os.getenv('LOGIN_TR')
PASS_TR = os.getenv('PASS_TR')
LOGIN_CN = os.getenv('LOGIN_CN')
PASS_CN = os.getenv('PASS_CN')

class Booking:
    def __init__(self, country="TURKEY"):
        self.login = LOGIN_TR if country == "TURKEY" else LOGIN_CN
        self.password = PASS_TR if country == "TURKEY" else PASS_CN
        self.base_url = "https://afl.booking-cargo.ru/"
        self.browser = None
        self.page = None

    async def launch_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def close_browser(self):
        if self.browser:
            await self.browser.close()

    async def login_portal(self, url=None):
        url = url or self.base_url
        await self.page.goto(url)
        await self.page.fill("input[type='text']", self.login)
        await self.page.fill("input[type='password']", self.password)
        await self.page.keyboard.press("Enter")

    async def available_flights(self, fr, to, day, month, aircrafts=['73H', '77W']):
        day = day[:2]
        month = month[2:]
        await self.launch_browser()
        await self.login_portal()
        flights = []

        try:
            await self.page.click("div.ant-col.ant-col-4.css-lked6w")
            await self.page.wait_for_selector("input")
            inputs = await self.page.query_selector_all("input")

            await inputs[5].click()
            await inputs[5].press("Enter")
            await self.page.wait_for_timeout(200)

            await inputs[8].fill(fr)
            await asyncio.sleep(.2)
            await inputs[8].press("Enter")
            await inputs[9].fill(to)
            await asyncio.sleep(.2)
            await inputs[9].press("Enter")
            await self.page.click("button:has-text('Выбрать рейс')")
            if await self.page.wait_for_selector('[class = "ant-table-row ant-table-row-level-0"]'):
                while True:
                    try:
                        rows = await self.page.query_selector_all('[class = "ant-table-row ant-table-row-level-0"]')
                        for row in rows:
                            tds = await row.query_selector_all("td")
                            date = await tds[2].inner_text()
                            flight_num = await tds[3].inner_text()
                            aircraft = await tds[8].inner_text()
                            availability = await tds[-1].inner_text()

                            if int(date[:2]) >= int(day) and availability != 'Занято' and aircraft in aircrafts:
                                if int(date[:2]) > int(day):
                                    raise StopIteration
                                flights.append((flight_num, availability, date[:2] + month.upper()))
                        next_page = await self.page.query_selector_all("li[class = 'ant-pagination-next ant-pagination-disabled']")
                        if len(next_page):
                            break
                        await self.page.click("span.anticon.anticon-right")
                        await self.page.wait_for_timeout(1000)
                    except StopIteration:
                        break
                    except Exception as e:
                        await asyncio.sleep(10)
        finally:
            await self.close_browser()

        return flights

    async def check(self, awb, message = None):
        await self.launch_browser()
        await self.login_portal(self.base_url + "booking")
        if message:
            prev[message.chat.id] = await message.answer(f'Processing ⏳{round(1/34*100, 2)}%⏳"')
        try:
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(10/34*100, 2)}%⏳"')
            await self.page.wait_for_selector("input")
            await self.page.get_by_placeholder('12345678').fill(awb[4:])
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(20/34*100, 2)}%⏳"')
            await self.page.click('[class = "ant-btn css-zxsuvd ant-btn-round ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-icon-only ant-btn-compact-item ant-btn-compact-last-item"]')
            await asyncio.sleep(3)
            status_el = await self.page.query_selector_all(
                '[class = "ant-descriptions-item-content"]'
            )
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(30/34*100, 2)}%⏳"')
            status = await status_el[20].inner_text()
        except Exception as e:
            status = "ND"
            print(e)
        finally:
            await self.close_browser()
            if message:
                await prev[message.chat.id].delete()
                del prev[message.chat.id]
        return status

    async def cancel(self, awb, message = None):
        await self.launch_browser()
        await self.login_portal(self.base_url + "booking")
        if message:
            prev[message.chat.id] = await message.answer(f'Processing ⏳{round(1/34*100, 2)}%⏳"')
        try:
            await self.page.wait_for_selector("input")
            await self.page.get_by_placeholder('12345678').fill(awb[4:])
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(10/34*100, 2)}%⏳"')
            await self.page.click('[class = "ant-btn css-zxsuvd ant-btn-round ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-icon-only ant-btn-compact-item ant-btn-compact-last-item"]')
            await self.page.wait_for_selector('[class = "ant-descriptions-item-content"]')
            await asyncio.sleep(1)
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(18/34*100, 2)}%⏳"')
            status_el = await self.page.query_selector_all(
                '[class = "ant-descriptions-item-content"]'
            )
            status = await status_el[20].inner_text()

            if status != "KK" and status != 'NN':
                return f"{awb}: not cancelable (status: {status})"
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(23/34*100, 2)}%⏳"')
            await self.page.click("button:has-text('Отменить бронь')")
            await self.page.wait_for_timeout(2000)
            await asyncio.sleep(3)
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(30/34*100, 2)}%⏳"')
            new_status_el = await self.page.query_selector_all(
                '[class = "ant-descriptions-item-content"]'
            )
            new_status = await status_el[20].inner_text()
        finally:
            await self.close_browser()
            await prev[message.chat.id].delete()
            del prev[message.chat.id]
        return f'{awb} cancelled: {new_status}'

    async def change(self, awb, fr=None, to=None, pcs=None, w=None, v=None, cargo=None, flight=None, day=None, month=None, message=None):
        db = get_db()
        day = day[:2]
        month = month[2:]
        if message:
            prev[message.chat.id] = await message.answer(f'Processing ⏳{round(1/34*100, 2)}%⏳"')

        await self.launch_browser()
        await self.login_portal(self.base_url + "booking")
        try:
            await self.page.wait_for_selector("input")
            await self.page.get_by_placeholder('12345678').fill(awb[4:])
            await self.page.click('[class = "ant-btn css-zxsuvd ant-btn-round ant-btn-primary ant-btn-color-primary ant-btn-variant-solid ant-btn-icon-only ant-btn-compact-item ant-btn-compact-last-item"]')

            await self.page.wait_for_selector('[class = "ant-descriptions-item-content"]')
            status_el = await self.page.query_selector_all('[class = "ant-descriptions-item-content"]')
            status = await status_el[20].inner_text()
            # previous_date = await status_el[18].inner_text()
            # previous_flight = await status_el[16].inner_text()

        except Exception as e:
            status = "ND"
            print(e)

        # if previous_date[:2] == day and previous_flight == flight and status != 'CN':
        #     return "The flight has not changed, please change the flight or leave it how it is"

        if message:
            await prev[message.chat.id].edit_text(f"Previous booking status:  <b>{status}</b> ⏳{round(15/34*100, 2)}%⏳")

        # Заполнить новые данные
        if pcs and w and v:
            edit_cargo_btn = await self.page.query_selector_all('[class = "anticon anticon-edit"]')
            await edit_cargo_btn[1].click()
            
            await self.page.locator('[id = "formBookingCreation_bookedPlacesQuantity"]').fill(pcs)
            await self.page.wait_for_timeout(100)
            await self.page.locator('[id = "formBookingCreation_bookedWeight"]').fill(w)
            await self.page.wait_for_timeout(100)
            await self.page.locator('[id = "formBookingCreation_bookedVolume"]').fill(v)
            await self.page.click('button[type = "submit"][class = "ant-btn css-lked6w ant-btn-primary ant-btn-color-primary ant-btn-variant-solid"]')
            
        if message:
            await prev[message.chat.id].edit_text(f"Previous booking status:  <b>{status}</b> ⏳{round(20/34*100, 2)}%⏳")

        # Нажать "Pick Flights"
        edit_cargo_btn = await self.page.query_selector_all('[class = "anticon anticon-edit"]') 
        await edit_cargo_btn[2].click()
        # await asyncio.sleep(.3)
        edit_cargo_btn = await self.page.query_selector_all('[class = "anticon anticon-edit"]') 
        await edit_cargo_btn[-1].click()
        if message:
            await prev[message.chat.id].edit_text(f"Searching for new flight: ⏳{round(26/34*100, 2)}%⏳")


        if flight and day:
            await asyncio.sleep(0.5)
            found = False
            i = 0
            while not found:
                i += 1
                frame = await self.page.query_selector('div[class = "ant-space css-lked6w ant-space-vertical ant-space-gap-row-small ant-space-gap-col-small FormBookingCargoUpload__SpaceStyled-cnRtNM ejwOjg"]')
                rows = await frame.query_selector_all('tr[class = "ant-table-row ant-table-row-level-0"]')
                selected_flight = await frame.query_selector_all('tr[class = "ant-table-row ant-table-row-level-0 ant-table-row-selected"]')
                if len(selected_flight):
                    selected_tds = await selected_flight[0].query_selector_all("td")
                    selected_num = await selected_tds[5].inner_text()
                    selected_date = await selected_tds[4].inner_text()

                    if selected_num == flight and selected_date[:2] == day:
                        if message:
                            await prev[message.chat.id].delete()
                            await self.close_browser()
                            return {'ffa': 'The flight was selected before! Please change the flight or leave as it is. The cargo info (pieces, weight and volume were applied)'}
        
                for row in rows:
                    tds = await row.query_selector_all("td")
                    date_text = await tds[2].inner_text()
                    flight_text = await tds[3].inner_text()
                    if date_text[:2] == day and flight_text.lower() == flight.lower():
                        await tds[0].click()
                        found = True
                        break
                if not found:
                    await asyncio.sleep(.3)
                    await self.page.click("li.ant-pagination-next")

                # if message:
                #     await prev[message.chat.id].edit_text(f"Searching for new flight: ⏳{round((29 + i)/34 * 100, 2)}%⏳")

            apply = await self.page.query_selector_all("button:has-text('Применить')")
            await apply[-1].click()
            save = await self.page.query_selector_all("button:has-text('Сохранить')")
            await save[-1].click()
            # await self.page.wait_for_timeout(1000)
            # await self.page.click("button:has-text('Сохранить и отправить')")

        # Получение итогов
        await asyncio.sleep(3)
        new_status_el = await self.page.query_selector_all('[class = "ant-descriptions-item-content"]')
        new_status = await new_status_el[20].inner_text()
        # await asyncio.sleep(5)
        flight_actual_el = await self.page.query_selector_all('[class = "ant-descriptions-item-content"]')
        flight_actual = await new_status_el[16].inner_text()

        awb_el = await self.page.query_selector_all('[class = "ant-descriptions-item-content"]')
        awb_actual = await new_status_el[0].inner_text()


        ffa = f"""FFA/4
{awb}{fr}{to}/T{pcs}K{w}MC{v}/{cargo}
{flight_actual}/{day}{month}/{fr}{to}/{new_status}
REF/CHACSSU""".upper()

        if message:
            await message.bot.send_message(chat_id=os.getenv("ADMIN_IDS")[0], text=f"{message.chat.full_name}:<code>{ffa}</code>")

        await db.update_awb(awb, ['booking_status', new_status])
        await db.update_awb(awb, ['flight', flight_actual])
        await db.update_awb(awb, ['date', day + month.upper()])

        if message:
            await prev[message.chat.id].delete()
            del prev[message.chat.id]
        await self.close_browser()
        return {
            "awb": awb_actual,
            "status": new_status,
            "flight": flight_actual,
            "ffa": ffa
        }

    async def book(self, fr, to, pcs, w, v, cargo, flight, day, month, message = None):
        db = get_db()
        await self.launch_browser()
        await self.login_portal()
        if message:
            prev[message.chat.id] = await message.answer(f'Processing ⏳{round(1/34*100, 2)}%⏳"')
        try:
            await self.page.click("div.ant-col.ant-col-4.css-lked6w")
            await self.page.wait_for_selector("input")
            inputs = await self.page.query_selector_all("input")
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(10/34*100, 2)}%⏳"')
            await inputs[4].click()
            await self.page.click("div:has-text('20250410_SA_200')[class = 'ant-select-item-option-content']")
            await asyncio.sleep(0.3)
            await inputs[5].click()
            await asyncio.sleep(0.3)
            await inputs[5].press("Enter")
            await self.page.wait_for_timeout(200)
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(15/34*100, 2)}%⏳"')
            await inputs[8].fill(fr)
            await inputs[8].press("Enter")
            await inputs[9].fill(to)
            await inputs[9].press("Enter")
            await inputs[11].click()
            await asyncio.sleep(.3)
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(17/34*100, 2)}%⏳"')
            await inputs[11].press("Enter")
            await inputs[12].fill(pcs)
            await inputs[12].press("Enter")
            await inputs[14].fill(w)
            await inputs[14].press("Enter")
            await inputs[16].fill(v)
            await inputs[16].press("Enter")

            textareas = await self.page.query_selector_all("textarea")
            await textareas[0].fill(cargo)
            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(18/34*100, 2)}%⏳"')
            await self.page.click("button:has-text('Выбрать рейс')")
            i = 0
            while True:
                rows = await self.page.query_selector_all("tr.ant-table-row")
                found = False
                for row in rows:
                    tds = await row.query_selector_all("td")
                    date_text = await tds[2].inner_text()
                    flight_text = await tds[3].inner_text()
                    if date_text[:2] == day and flight_text.lower() == flight.lower():
                        await tds[0].click()
                        found = True
                        break
                if found:
                    break
                if message:
                    await prev[message.chat.id].edit_text(f'Processing ⏳{round(18+i/34*100, 2)}%⏳"')
                    i += 1 
                await self.page.click("span.anticon.anticon-right")
                await asyncio.sleep(0.6)
            await self.page.click("button:has-text('Применить')")
            await self.page.wait_for_timeout(1000)
            await self.page.click("button:has-text('Сохранить и отправить')")
            
            await self.page.wait_for_selector('[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm ButtonLink__ButtonStyled-eeryZM gvPyWL"]')
            flight_el = await self.page.query_selector('a[class = "ant-btn css-lked6w ant-btn-link ant-btn-color-primary ant-btn-variant-link ant-btn-sm ButtonLink__ButtonStyled-eeryZM gvPyWL"]')
            flight_text = await flight_el.inner_text()

            if message:
                await prev[message.chat.id].edit_text(f'Processing ⏳{round(32/34*100, 2)}%⏳"')

            awb_num_el = await self.page.query_selector(".ant-descriptions-item-content")
            awb_num = await awb_num_el.inner_text()

            status_el = await self.page.query_selector_all('[class = "ant-descriptions-item-content"]')
            status = await status_el[20].inner_text()
        except Exception as e:
            print(e)
        finally:
            if message:
                await prev[message.chat.id].delete()
                del prev[message.chat.id]
            await self.close_browser()

        await db.update_awb(f"ID{message.chat.id}", ("booking_status", status))
        return {
            "awb": awb_num,
            "flight": flight_text,
            "status": status,
            "ffa": f"""FFA/4
{awb_num}{fr}{to}/T{pcs}K{w}MC{v}/{cargo}
{flight_text}/{day}{month}/{fr}{to}/{status}
REF/CHACSSU""".upper()
        }

# if __name__ == '__main__':
#     bk = Booking()
#     # print(asyncio.run(bk.check('555-10217760')))
# #     # print(asyncio.run(bk.cancel('555-10217760')))
# #     # print(asyncio.run(bk.available_flights('ist', "svo", '29', 'mar')))
# #     # print(asyncio.run(bk.change(awb='555-10217760', fr = 'ist', to='svo', cargo='SPP', flight='SU2137', day='10', month='apr')))
#     print(asyncio.run(bk.book('ist', 'svo', '1', '1', '0.01', 'SPP', 'SU2133', '25', 'apr')))