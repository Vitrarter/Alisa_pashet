from flask import Flask, request
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']  # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        # созда\м словарь в который в будущем положим имя пользователя
        sessionStorage[user_id] = {
            'first_name': None,
            'suggests': [
                "Мужигу",
                "Бабе",
                "Взрослому",
                "Ребенку",
                "F",
                "f"
            ]
        }
        return
    res['response']['text'] = 'Кому вы хотите подарить подарок?'
    if req['request']['original_utterance'].lower() in [
        'мужигу',
        'мужчине',
        'пацану',
        'парню',
        'мальчику',
        'сыну'
    ]:
        res['response']['text'] = 'Сколько ему лет?'
        res['response']['buttons'] = get_suggests(user_id)
        a = 0
        return
    elif req['request']['original_utterance'].lower() in [
        'бабе',
        'женщине',
        'феминистке',
        'девушке',
        'девочке',
        'дочке'
    ]:
        res['response']['text'] = 'Сколько ей лет?'
        res['response']['buttons'] = get_suggests(user_id)
        a = 1
        return
    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    # Подумайте, всё ли в этом фрагменте написано "красиво"?
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я покупаю',
        'я куплю'
    ]:

        res['response']['text'] = 'Вот что удалось подобрать!'
        res['response']['end_session'] = True
        return



    res['response']['buttons'] = get_suggests(user_id)  # Функция возвращает две подсказки для ответа.


def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][2:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Перейти",
            "url": "https://m.vk.com/id242062417",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
