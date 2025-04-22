import asyncpg
import asyncio


class Db:
    def __init__(self, dsn='postgresql://tesis_booking:1405@localhost/booking'):
        self.dsn = dsn
        self.pool = None

    async def init(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        await self.create_users()
        await self.create_awb()
        await self.create_available_flights()

    async def create_users(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id serial PRIMARY KEY, 
                    user_id VARCHAR(50) UNIQUE NOT NULL, 
                    username VARCHAR(50) NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL
                );
            """)
            print('all good')

    async def create_awb(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS awb (
                    id serial PRIMARY KEY, 
                    awb VARCHAR(12) UNIQUE NOT NULL,
                    pieces VARCHAR NOT NULL,
                    weight VARCHAR NOT NULL,
                    volume VARCHAR NOT NULL,
                    cargo VARCHAR NOT NULL,
                    departure VARCHAR(3) NOT NULL,
                    destination VARCHAR(3) NOT NULL,
                    flight VARCHAR(6) NOT NULL,
                    date VARCHAR(5) NOT NULL,
                    booking_status VARCHAR(2) NOT NULL,
                    arrival_status VARCHAR NOT NULL,
                    client VARCHAR NOT NULL,
                    user_id VARCHAR REFERENCES customers(user_id)
                );
            """)

    async def create_available_flights(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS available_flights (
                    id serial PRIMARY KEY,
                    updated VARCHAR NOT NULL,
                    flight VARCHAR(6) NOT NULL,
                    departure VARCHAR(3) NOT NULL,
                    destination VARCHAR(3) NOT NULL,
                    date VARCHAR NOT NULL,
                    status VARCHAR NOT NULL,
                    UNIQUE(flight, departure, destination, date)
                );
            """)

    async def insert_user(self, user_id, username, first_name, last_name):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO customers (user_id, username, first_name, last_name)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO NOTHING;
                """, str(user_id), username, first_name, last_name)
                print("Пользователь успешно добавлен")
        except Exception as e:
            print(f'Error: {e}')

    async def insert_awb(self, awb, pieces, weight, volume, cargo, departure, destination, flight, date, booking_status, arrival_status, client, user_id):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO awb (awb, pieces, weight, volume, cargo, departure, destination, flight, date, booking_status, arrival_status, client, user_id)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13);
                """, awb, pieces, weight, volume, cargo.upper(), departure.upper(), destination.upper(), flight.upper(), date, booking_status.upper(), arrival_status.upper(), client.upper(), str(user_id))
        except Exception as e:
            print(f'Error: {e}')

    async def delete_awb(self, awb):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    delete from awb where awb =
                    $1;
                """, awb)
        except Exception as e:
            print(f'Error: {e}')
    
    async def update_awb(self, awb, upd_val):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(f"""
                    UPDATE awb SET {upd_val[0]} = $1 WHERE awb = $2;
                """, str(upd_val[1]).upper(), awb)
        except Exception as e:
            print(f'Error: {e}')

    async def ins_upd_available_flight(self, updated, flight, departure, destination, date, status):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO available_flights (updated, flight, departure, destination, date, status)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (flight, departure, destination, date) DO UPDATE
                    SET updated = $1, date = $5, status = $6;
                """, updated, flight.upper(), departure.upper(), destination.upper(), date, status.upper())
        except Exception as e:
            print(f'Error: {e}')

    async def get_awbs(self, val, user_id):
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(f"""
                    SELECT {val} FROM awb WHERE user_id = $1 ORDER BY id DESC;
                """, str(user_id))
                return [r[val] for r in rows]
        except Exception as e:
            print(f'Error: {e}')
            return []

    async def get_awb_info(self, val, awb, user_id):
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(f"""
                    SELECT {val} FROM awb WHERE user_id = $1 AND awb = $2 ORDER BY id DESC;
                """, str(user_id), str(awb))
                return row[val] if row else None
        except Exception as e:
            print(f'Error: {e}')
            return None

    async def get_not_arrived(self):
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT awb FROM awb WHERE arrival_status IN ('ND', 'NO DATA');
                """)
                return [r['awb'] for r in rows]
        except Exception as e:
            print(f'Error: {e}')
            return []

    async def get_not_booked(self):
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT awb FROM awb WHERE booking_status != 'KK';
                """)
                return [r['awb'] for r in rows]
        except Exception as e:
            print(f'Error: {e}')
            return []

    async def get_available_flights(self, date, departure, destination):
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT flight, status FROM available_flights
                    WHERE date = $1 AND departure = $2 AND destination = $3;
                """, str(date)[:2], departure, destination)
                return [(r['flight'], r['status']) for r in rows]
        except Exception as e:
            print(f'Error: {e}')
            return []


# async def main():
#     db = Db()
#     await db.init()
#     await db.insert_user("123", "username", "first", "last")

# asyncio.run(main())
