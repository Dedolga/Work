import psycopg2

conn = psycopg2.connect(database='data_bd', user='postgres', password='90Olgabase23')
conn.autocommit = True

def create_table_userdata():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS userdata(id serial,
            vk_id varchar(50) not null primary key);"""
    )

def create_table_processed_users():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS processed_users(
            id serial,
            vk_id varchar(50) primary key);"""
        )

def insert_userdata(vk_id):
    with conn.cursor() as cur:
       cur.execute(
             f"""INSERT INTO userdata (vk_id)
           VALUES ('{vk_id}') ON CONFLICT(vk_id) DO NOTHING;"""
          )
    print('Данные в таблицу пользователей успешно внесены')

def insert_processed_users(vk_id):
    with conn.cursor() as cur:
        cur.execute(
            f"""INSERT INTO processed_users (vk_id)
           VALUES ('{vk_id}')"""
        )
    print('Данные в таблицу обработанных пользователей успешно внесены')

def select():
    with conn.cursor() as cur:
        cur.execute(f"""SELECT u.vk_id, pu.vk_id
                        FROM userdata AS u LEFT JOIN processed_users AS pu 
                        ON u.vk_id = pu.vk_id
                        WHERE pu.vk_id IS NULL;""")
        return cur.fetchone()


def create_tables():
    create_table_userdata()
    create_table_processed_users()

