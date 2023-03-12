import vk_api
import datetime
from random import randrange
from d_b import *
from vk_api.longpoll import VkLongPoll, VkEventType

user_token = 'vk1.a.Qfppwb3Q_bttT3ADtH7yXL56iNu_1y4Hql6zLaR4-JyBqAZptm20gfD6ikZ1ywa-B11YXtBkA1Lc-8-qH08dneVfYjKKwiSCRKFCpkz4CB8R5UCpdzbJp-1i1ANv77tdATBmbGE442wz2_66gVUW15eN4jRUHxI3JoazX7gpXC6LKBzl_wn9tReMZiA2FzDaZhHVxSB25U1Lye9-D-Iirw'
comm_token = 'vk1.a.830rM18zA0ACh-nDrntjq-vsZub2CasfPrL-oWCIBjDGeDBLDf0tUlugxOF_wPWFNEdYxdj8NX6R9dqF6h-6kvW61F01SiftnbGBxmTlwBykvr42K_kK7WWjnqofieNCE1DGpqcBLaTpAq5urGkVl3GhHlewqglDvW6wjtvmWw73L9-CoirxdFS9UcPOyU_FjGIpu5rSytX3FDZitUXPUA'

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


def get_sender_data(user_id):
    sender_data={}
    response = vk1.method('users.get', {'access_token': user_token,
                                        'user_id': user_id,
                                        'v': '5.131',
                'fields': 'first_name, last_name, bdate, sex, city'})
    if response:
        for key, value in response[0].items():
            if key=='city':
                sender_data[key]=value['id']
            else:
                sender_data[key]=value
        for key, value in sender_data.items():
            if key == 'bdate':
                sender_data[key] = datetime.datetime.now().year - int(value[-4:])
        for key, value in sender_data.items():
            if key == 'sex':
                if value == 1:
                    sender_data[key] = 2
                else:
                    sender_data[key] = 1
    return sender_data

def get_sender_name(user_id):
    dict = get_sender_data(user_id)
    first_name = ' '
    for key, value in dict.items():
        if key =='first_name':
            first_name = dict['first_name']
    return first_name

def get_city(user_id):
    sender_data = get_sender_data(user_id)
    return sender_data['city']

def get_user_age(user_id):
    sender_data = get_sender_data(user_id)
    return sender_data['bdate']

def get_user_sex(user_id):
    sender_data = get_sender_data(user_id)
    return sender_data['sex']

def get_add_info(user_id, field):
    dict_info = {
        'bdate': 'Введите Вашу дату рождения в формате ДД.ММ.ГГГГ',
        'city': 'Введите Ваш город'}
    write_msg(user_id, f"Недостаточно данных, введите их: \n {dict_info[field]}")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if field == 'city':
                    return get_city(user_id)
                elif field == 'bdate':
                    if len(event.text.split('.')) != 3:
                        write_msg(user_id, 'Дата рождения не верна!')
                        return False
                    return event.text


def find_user(user_id):
    link='vk.com/id'
    response = vk2.method('users.search', {'v': 5.131,
                                           'sex': get_user_sex(user_id),
            'age_from': get_user_age(user_id)-5,
            'age_to': get_user_age(user_id)+5,
            'city': get_city(user_id),
            'fields': 'is_closed, id, first_name, last_name',
            'has photo': 1,
            'status': 6,
            'count': 500})
    for one in response['items']:
        if one.get('is_closed') == False:
            first_name = one.get('first_name')
            last_name=one.get('last_name')
            vk_id = str(one.get('id'))
            vk_link = link + str(one.get('id'))
            insert_userdata(first_name, last_name, vk_id, vk_link)
        else:
           continue
    return f'Поиск окончен'

def get_photo(user_id):
    responses = vk2.method('photos.get',{'access_token': user_token,
                                      'v': '5.131',
                                      'owner_id': user_id,
                                      'album_id': 'profile',
                                      'count': 25,
                                      'extended': 1})
    list_p = []
    photo_dict = {}
    if responses.get('count'):
        list_p = sorted(responses.get('items'), key=lambda x: x['likes']['count']+ x['comments']['count'], reverse = True)[:3]
        photo_dict = {'user_id': list_p[0]['owner_id'], 'photo_ids':[]}
    for p in list_p:
        photo_dict['photo_ids'].append(p['id'])
    return photo_dict['photo_ids']

def show_photo(user_id, message, offset):
    photo_list_ids = get_photo(choosen_user_id(offset))
    if len(photo_list_ids) == 0:
        attachment = 0
    if len(photo_list_ids) == 1:
        attachment = f'photo{choosen_user_id(offset)}_{photo_list_ids[0]}'
    if len(photo_list_ids) == 2:
        attachment = f'photo{choosen_user_id(offset)}_{photo_list_ids[0]},photo{choosen_user_id(offset)}_{photo_list_ids[1]}'
    if len(photo_list_ids) >= 3:
        attachment = f'photo{choosen_user_id(offset)}_{photo_list_ids[0]},photo{choosen_user_id(offset)}_{photo_list_ids[1]},photo{choosen_user_id(offset)}_{photo_list_ids[2]}'
    response = vk1.method('messages.send', {'user_id': user_id,
                                        'access_token': user_token,
                                        'attachment': attachment,
                                        'message': 'Фотографии',
                                        'random_id': 0})
    return response


def choose_users(user_id, offset):
    write_msg(user_id, choosen_user(offset))
    choosen_user_id(offset)
    insert_processed_users(choosen_user_id(offset), offset)
    get_photo(choosen_user_id(offset))
    show_photo(user_id, 'Фото', offset)

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
    get_sender_data()
    get_sender_name()
    get_user_age()
    get_user_sex()
    get_city()
    get_add_info()
    find_user()
    get_photo()
    show_photo()
    choose_users()
    choosen_user()
    choosen_user_id()
