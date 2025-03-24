import psycopg2

class Db():
    def __init__(self):
        try:
            self.conn = psycopg2.connect(dbname='booking', user='tesis_booking', 
                                    password='1405', host='localhost')
            print("Information on PostgreSQL server")
            print(self.conn.get_dsn_parameters(), "\n")
        except:
            print('smt went wrong')
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        self.create_users()
        self.create_awb()

    def create_users(self):
        self.cursor.execute("""create table if not exists customers(
                    id serial primary key, 
                    user_id varchar(50) unique not null, 
                    username varchar(50) not null,
                    first_name varchar(50) not null,
                    last_name varchar(50) not null
                            );
                            """)
    
    def create_awb(self):
        self.cursor.execute("""create table if not exists awb(
                    id serial primary key, 
                    awb varchar(12) unique not null,
                    flight varchar(6) not null,
                    date varchar(5) not null,
                    booking_status varchar(2) not null,
                    arrival_status varchar not null,
                    user_id varchar references customers(user_id) 
                            );
                            """)
    

        # self.cursor.execute("insert into users (user_id, username) values ('Tom', 33);")
        # self.cursor.execute('select * from users;')
        # print(self.cursor.fetchall())
    
    
    def insert_user(self, user_id, username, first_name, last_name):
        try:
            self.cursor.execute(f"insert into customers (user_id, username, first_name, last_name) values ({user_id}, '{username}', '{first_name}','{last_name}');")
            print("Пользователь успешно добавлен")
        except:
            pass
    
    def insert_awb(self, awb, flight, date,  booking_status, arrival_status, user_id):
        try:
            self.cursor.execute(f"insert into awb (awb, flight, date, booking_status, arrival_status, user_id) values ('{awb}', '{flight}', '{date}', '{booking_status}','{arrival_status}', '{user_id}');")
            print("update")
        except:
            pass
    
    def update_awb(self, awb, upd_val):
        try:
            self.cursor.execute(f"update awb set {upd_val[0]} = '{upd_val[1]}' where awb = '{awb}';")
            print("update")
        except:
            pass
    
    def get_awbs(self, val, user_id):
        awbs = []
        try:
            self.cursor.execute(f"select {val} from awb where user_id = '{user_id}' ORDER BY id desc")
            for el in self.cursor.fetchall():
                awbs.append(el)
            return awbs
        except:
            print('get awb err')
            pass
    
    def get_awb_info(self, val, awb, user_id):
        awbs = []
        try:
            self.cursor.execute(f"select {val} from awb where user_id = '{user_id}' and awb = '{awb}' ORDER BY id desc")
            for el in self.cursor.fetchall():
                awbs.append(el)
            return awbs
        except:
            print('get awb err')
            pass
    
    def get_not_arrived(self):
        awbs = []
        try:
            self.cursor.execute(f"select awb from awb where arrival_status = 'ND' or arrival_status = 'NO DATA'")
            for el in self.cursor.fetchall():
                awbs.append(el)
            return awbs
        except:
            print('get awb err')
            pass