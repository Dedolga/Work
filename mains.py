import vk_api
import datetime
from random import randrange
from d_b import *
from vk_api.longpoll import VkLongPoll, VkEventType

user_token = ''
comm_token = ''

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
    sender_data = {}
    response = vk1.method('users.get', {'access_token': user_token,
                                        'user_id': user_id,
                                        'v': '5.131',
                'fields': 'first_name, last_name, bdate, sex, city'})
    try:
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
    except KeyError:
        return None

def get_sender_name(user_id):
    dict = get_sender_data(user_id)
    first_name = ' '
    for key, value in dict.items():
        if key =='first_name':
            first_name = dict['first_name']
    return first_name


def get_add_info(user_id, field):
    sender_data = get_sender_data(user_id)
    dict_info = {
        'bdate': 'Введите Вашу дату рождения в формате ДД.ММ.ГГГГ',
        'city': 'Введите Ваш город'}
    write_msg(user_id, f"Недостаточно данных, введите их: \n {dict_info[field]}")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if field == 'city':
                    return sender_data['city']
                elif field == 'bdate':
                    if len(event.text.split('.')) != 3:
                        write_msg(user_id, 'Дата рождения не верна!')
                        return False
                    return event.text

def find_user(user_id):
    global user_info_list
    user_info_list = []
    link='vk.com/id'
    sender_data = get_sender_data(user_id)
    user_info=[]
    response = vk2.method('users.search', {'v': 5.131,
                                           'sex': sender_data['sex'],
            'age_from': sender_data['bdate']-5,
            'age_to': sender_data['bdate']+5,
            'city': sender_data['city'],
            'fields': 'is_closed, id, first_name, last_name',
            'has photo': 1,
            'status': 6,
            'count': 500})
    try:
       one = response['items']
    except KeyError:
        return None
    for one in response['items']:
        if one.get('is_closed') == False:
            vk_id = str(one.get('id'))
            person =[
            one.get('first_name'),
            one.get('last_name'),
            str(one.get('id')),
            link + str(one.get('id'))]
            user_info_list.append(person)
            insert_userdata(vk_id)
    return user_info_list

def get_photo(user_id):
    responses = vk2.method('photos.get',{'access_token': user_token,
                                      'v': '5.131',
                                      'owner_id': user_id,
                                      'album_id': 'profile',
                                      'count': 25,
                                      'extended': 1})
    list_p = []
    photo_dict = {}
    try:
        if responses.get('count'):
            list_p = sorted(responses.get('items'), key=lambda x: x['likes']['count']+ x['comments']['count'], reverse = True)[:3]
            photo_dict = {'user_id': list_p[0]['owner_id'], 'photo_ids':[]}
        for p in list_p:
            photo_dict['photo_ids'].append(p['id'])
        return photo_dict['photo_ids']
    except KeyError:
        return None

def show_photo(user_id, message):
    photo_list_ids = get_photo(choosen_user_id())
    if len(photo_list_ids) == 0:
        attachment = 0
    if len(photo_list_ids) == 1:
        attachment = f'photo{choosen_user_id()}_{photo_list_ids[0]}'
    if len(photo_list_ids) == 2:
        attachment = f'photo{choosen_user_id()}_{photo_list_ids[0]},photo{choosen_user_id()}_{photo_list_ids[1]}'
    if len(photo_list_ids) >= 3:
        attachment = f'photo{choosen_user_id()}_{photo_list_ids[0]},photo{choosen_user_id()}_{photo_list_ids[1]},photo{choosen_user_id()}_{photo_list_ids[2]}'
    response = vk1.method('messages.send', {'user_id': user_id,
                                        'access_token': user_token,
                                        'attachment': attachment,
                                        'message': 'Фотографии',
                                        'random_id': 0})
    return response

def choose_users(user_id):
    if choosen_user_id() == None:
        write_msg(user_id,  f'Анкет больше не осталось, необходим новый поиск ')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                find_user(user_id)
                write_msg(event.user_id, f'Жми на кнопку "Еще", чтобы увидеть другие варианты')
                choose_users(user_id)
                return
    else:
        write_msg(user_id, choosen_user())
        choosen_user_id()
        get_photo(choosen_user_id())
        show_photo(user_id, 'Фотографии')


def choosen_user():
    insert_processed_users(choosen_user_id())
    person_id = choosen_user_id()
    for i in user_info_list:
        if person_id == i[2]:
            return f'ссылка на профиль - {i[3]}, {i[0]} {i[1]}'
    return f'ссылка на профиль - {i[3]}, {i[0]} {i[1]}'


def choosen_user_id():
    tuple_person = select()
    choosen_user_list = []
    for each in tuple_person:
        choosen_user_list.append(each)
        for i in choosen_user_list:
            return str(i)

def main():
    write_msg()
    get_sender_data()
    get_sender_name()
    get_add_info()
    find_user()
    get_photo()
    show_photo()
    choose_users()
    choosen_user()
    choosen_user_id()

