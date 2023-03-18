import psycopg2
from mains import *

conn = psycopg2.connect(database='data_bd', user='postgres', password='90Olgabase23')
conn.autocommit = True

def create_table_userdata():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS userdata(id serial, 
            first_name varchar(40) not null,
            last_name varchar(30) not null, 
            vk_id varchar(30) not null primary key, 
            vk_link varchar(60));"""
        )

def create_table_processed_users():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS processed_users(
            id serial,
            puvk_id varchar(60) primary key);"""
        )

def insert_userdata(first_name, last_name, vk_id, vk_link):
    with conn.cursor() as cur:
        cur.execute(
                f"""INSERT INTO userdata (first_name, last_name, vk_id, vk_link) 
            VALUES ('{first_name}', '{last_name}', '{vk_id}', '{vk_link}') ON CONFLICT(vk_id) DO UPDATE SET
            first_name = '{first_name}', last_name = '{last_name}', vk_link = '{vk_link}';"""
            )
    print('Данные в таблицу пользователей успешно внесены')

def insert_processed_users(puvk_id, offset):
    with conn.cursor() as cur:
        cur.execute(
            f"""INSERT INTO processed_users (puvk_id) 
            VALUES ('{puvk_id}')
            OFFSET '{offset}';"""
        )
    print('Данные в таблицу обработанных пользователей успешно внесены')

def select(offset):
    with conn.cursor() as cur:
        cur.execute(f"""SELECT u.first_name, u.last_name, u.vk_id, u.vk_link FROM userdata AS u
                        LEFT JOIN processed_users AS pu ON u.vk_id = pu.puvk_id WHERE pu.puvk_id IS NULL OFFSET '{offset}';""")
        return cur.fetchone()


def creating_database():
    create_table_userdata()
    create_table_processed_users()

