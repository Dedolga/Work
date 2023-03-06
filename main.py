import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from d_b import *

user_token = ''
comm_token = ''

offset = 10
line = range(0, 1000)

vk1 = vk_api.VkApi(token=comm_token)
vk2 = vk_api.VkApi(token=user_token)

longpoll = VkLongPoll(vk1)
print('Chat bot is ready')

def write_msg(user_id, message):
    vk1.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': randrange(10 ** 7)})

def get_sender_name(user_id):
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': user_token,
                'user_ids': user_id,
                'v': '5.131'}
    r = requests.get(url, params=params)
    response = r.json()
    try:
        user_dict = response['response']
        for each in user_dict:
            for key, value in each.items():
                first_name = each.get('first_name')
                return first_name
    except KeyError:
        write_msg(user_id, 'Ошибка: user_token')

def get_user_age(user_id):
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': user_token,
              'user_ids': user_id,
              'fields': 'bdate',
              'v': '5.131'}
    r = requests.get(url, params=params)
    response = r.json()
    try:
        user_list_bdate = response['response']
        for each in user_list_bdate:
            for key, value in each.items():
                bdate = each.get('bdate')
                return datetime.datetime.now().year-int(bdate[-4:])
                #print(get_user_age(user_id))
    except KeyError:
        write_msg(user_id, 'Ошибка: user_token')


def get_user_sex(user_id):
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': user_token,
            'user_ids': user_id,
            'fields': 'sex',
            'v': '5.131'}
    r = requests.get(url, params=params)
    response = r.json()
    try:
        user_list = response['response']
        for each in user_list:
            if each.get('sex') == 2:
                find_sex = 1
                return find_sex
            elif each.get('sex') == 1:
                find_sex = 2
                return find_sex
    except KeyError:
        write_msg(user_id, 'Ошибка: user_token')


def city_id(user_id, city_name):
    url = url = f'https://api.vk.com/method/database.getCities'
    params = {'access_token': user_token,
            'country_id': 1,
            'q': f'{city_name}',
            'need_all': 0,
            'count': 500,
            'v': '5.131'}
    r = requests.get(url, params=params)
    response = r.json()
    try:
        inform_list = response['response']
        list_cities = inform_list['items']
        for each in list_cities:
            found_city_name = each.get('title')
            if found_city_name == city_name:
                found_city_id = each.get('id')
                return int(found_city_id)
    except KeyError:
        write_msg(user_id, 'Ошибка: user_token')

def get_city(user_id):
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': user_token,
            'fields': 'city',
            'user_ids': user_id,
            'v': '5.131'}
    r = requests.get(url, params=params)
    response = r.json()
    try:
        inform_dict = response['response']
        for each in inform_dict:
            if 'city' in each:
                city = each.get('city')
                id = str(city.get('id'))
                return id
            elif 'city' not in each:
                write_msg(user_id, 'Введите Ваш город: ')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        city_name = event.text
                        id_city = city_id(user_id, city_name)
                        if id_city != '' or id_city != None:
                            return str(id_city)
                        else:
                            break
    except KeyError:
        write_msg(user_id, 'Ошибка: user_token')

def get_add_info(user_id, field):
    dict_info = {
    'bdate': 'Введите Вашу дату рождения в формате ДД.ММ.ГГГГ',
    'city': 'Введите Ваш город'}
    write_msg(user_id, f"Недостаточно данных, введите их: \n {dict_info[field]}")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if field =='city':
                    return get_city(user_id)
                elif field =='bdate':
                    if len(event.text.split('.'))!=3:
                        write_msg(user_id, 'Дата рождения не верна!')
                        return False
                    return event.text

def find_user(user_id):
    url = f'https://api.vk.com/method/users.search'
    params = {'access_token': user_token,
            'v': '5.131',
            'sex': get_user_sex(user_id),
            'age_from': get_user_age(user_id)-5,
            'age_to': get_user_age(user_id)+5,
            'city': get_city(user_id),
            'fields': 'is_closed, id, first_name, last_name',
            'status': 6,
            'count': 500}
    r = requests.get(url, params=params)
    resp_json = r.json()
    try:
        dictionary = resp_json['response']
        list_inform = dictionary['items']
        for dict_persons in list_inform:
            if dict_persons.get('is_closed') == False:
                first_name = dict_persons.get('first_name')
                last_name = dict_persons.get('last_name')
                vk_id = str(dict_persons.get('id'))
                vk_link = 'vk.com/id' + str(dict_persons.get('id'))
                insert_userdata(first_name, last_name, vk_id, vk_link)
            else:
                continue
        return f'Поиск окончен'
    except KeyError:
        write_msg(user_id, 'Ошибка: user_token')

def get_photo(user_id):
    url = 'https://api.vk.com/method/photos.getAll'
    params = {
                                  'access_token': user_token,
                                  'v': '5.131',
                                  'owner_id': user_id,
                                  'album_id': 'profile',
                                  'count': 25,
                                  'extended': 1,
                              }
    r = requests.get(url, params=params)
    photos_dict = dict()
    r_json = r.json()
    try:
        dictionary_p = r_json['response']
        list_p = dictionary_p['items']
        for each in list_p:
            photos_id = str(each.get('id'))
            i_likes = each.get('likes')
            if i_likes.get('count'):
                likes = i_likes.get('count')
                photos_dict[likes] = photos_id
        list_ids = sorted(photos_dict.items(), reverse=True)
        return list_ids
    except KeyError:
        write_msg(user_id, 'Ошибка user_token')

def get_photo_1(user_id):
    photo_list = get_photo(user_id)
    count = 0
    for each in photo_list:
        count += 1
        if count == 1:
            return each[1]

def get_photo_2(user_id):
    photo_list = get_photo(user_id)
    count = 0
    for each in photo_list:
        count += 1
        if count == 2:
            return each[1]

def get_photo_3(user_id):
    photo_list = get_photo(user_id)
    count = 0
    for each in photo_list:
        count += 1
        if count == 3:
            return each[1]

def show_photo_1(user_id, message, offset):
    vk1.method('messages.send', {'user_id': user_id,
                                'access_token': user_token,
                                'attachment': f'photo{choosen_user_id(offset)}_{get_photo_1(choosen_user_id(offset))}',
                                'message': message,
                                'random_id': 0})

def show_photo_2(user_id, message, offset):
    vk1.method('messages.send', {'user_id': user_id,
                                'access_token': user_token,
                                'attachment': f'photo{choosen_user_id(offset)}_{get_photo_2(choosen_user_id(offset))}',
                                'message': message,
                                'random_id': 0})

def show_photo_3(user_id, message, offset):
    vk1.method('messages.send', {'user_id': user_id,
                                'access_token': user_token,
                                'attachment': f'photo{choosen_user_id(offset)}_{get_photo_3(choosen_user_id(offset))}',
                                'message': message,
                                'random_id': 0})

def choose_users(user_id, offset):
    write_msg(user_id, choosen_user(offset))
    choosen_user_id(offset)
    insert_processed_users(choosen_user_id(offset), offset)
    get_photo(choosen_user_id(offset))
    show_photo_1(user_id, 'Фото 1', offset)
    if get_photo_2(choosen_user_id(offset)) != None:
        show_photo_2(user_id, 'Фото 2', offset)
        show_photo_3(user_id, 'Фото 3', offset)
    else:
        write_msg(user_id, f'Фотографий больше нет')

def choosen_user(offset):
    tuple_person = select(offset)
    choosen_list = []
    for each in tuple_person:
        choosen_list.append(each)
    return f'ссылка на профиль - {choosen_list[3]}, {choosen_list[0]} {choosen_list[1]}'

def choosen_user_id(offset):
    tuple_person = select(offset)
    choosen_user_list = []
    for each in tuple_person:
        choosen_user_list.append(each)
    return str(choosen_user_list[2])

def main():
    write_msg()
    get_sender_name()
    get_user_age()
    get_user_sex()
    city_id()
    get_city()
    get_add_info()
    find_user()
    get_photo()
    get_photo_1()
    get_photo_2()
    get_photo_3()
    show_photo_1()
    show_photo_2()
    show_photo_3()
    choose_users()
    choosen_user()
    choosen_user_id()