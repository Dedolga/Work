from main import *
import json


def create_button(text, color):
    return {"action": {"type": "text", "label": f"{text}"}, "color": f"{color}"}
keyboard = {
        "one_time": False,
        "buttons": [[{"action": {"type": "text", "payload": "{\"button\":\"btn_1\"}", "label": "Поиск пары"}, "color": "primary"}],
                    [{"action": {"type": "text", "payload": "{\"button\":\"btn_2\"}", "label": "Еще"}, "color": "secondary"}]]}

def searcher_data(user_id, text):
    vk1.method('messages.send', {'user_id': user_id,
                                    'message': text,
                                    'random_id': 0,
                                    'keyboard': keyboard})

keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = int(event.user_id)
        msg = event.text.lower()
        searcher_data(user_id, msg.lower())
        if request == 'поиск пары':
            creating_database()
            write_msg(user_id, f'Привет, {get_sender_name(user_id)}')
            find_user(user_id)
            write_msg(event.user_id, f'Жми на кнопку "Еще", чтобы увидеть другие варианты')
            choose_users(user_id, offset)

        elif request == 'еще':
            for i in line:
                offset += 1
                choose_users(user_id, offset)
                break

        else:
            write_msg(event.user_id, 'Попробуйте ввести сообщение еще раз')
