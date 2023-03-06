import psycopg2

conn = psycopg2.connect(database='data_bd', user='postgres', password='')


def create_table_userdata():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS userdata(id serial, 
            first_name varchar(40) not null,
            last_name varchar(30) not null, 
            vk_id varchar(30) not null primary key, 
            vk_link varchar(60));"""
        )
        conn.commit()
    print('Таблица с пользователями создана')


def create_table_processed_users():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS processed_users(
            id serial,
            vk_id varchar(60) primary key);"""
        )
        conn.commit()
    print('Таблица с обработанными пользователями создана')


def insert_userdata(first_name, last_name, vk_id, vk_link):
    with conn.cursor() as cur:
        cur.execute(
                f"""INSERT INTO userdata (first_name, last_name, vk_id, vk_link) 
            VALUES ('{first_name}', '{last_name}', '{vk_id}', '{vk_link}');"""
            )
        conn.commit()
    print('Данные в таблицу пользователей успешно внесены')

def insert_processed_users(vk_id, offset):
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO processed_users (vk_id) 
            VALUES ('{vk_id}')
            OFFSET '{offset}';"""
        )
        conn.commit()
    print('Данные в таблицу обработанных пользователей успешно внесены')

def select(offset):
    with conn.cursor() as cur:
        cur.execute(f"""SELECT u.first_name, u.last_name, u.vk_id, u.vk_link, pu.vk_id FROM userdata AS u
                        LEFT JOIN processed_users AS pu ON u.vk_id = pu.vk_id WHERE pu.vk_id IS NULL OFFSET '{offset}';""")
        return cur.fetchone()


def drop_table_userdata():
    with conn.cursor() as cur:
        cur.execute(
            """DROP TABLE IF EXISTS userdata CASCADE;"""
        )
        conn.commit()
        print('Таблица с пользователями удалена')


def drop_table_processed_users():
    with conn.cursor() as cur:
        cur.execute(
            """DROP TABLE  IF EXISTS processed_users CASCADE;"""
        )
        conn.commit()
        print('Таблица с обработанными пользователями удалена')


def creating_database():
    drop_table_userdata()
    drop_table_processed_users()
    create_table_userdata()
    create_table_processed_users()
