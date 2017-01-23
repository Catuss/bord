from random import randint

sid = 'yoba_id'


def set_sid(request):
    """
    По реквесту, устанавливает пользователю в куки сессию с ключем 
    Используется для определения ОП'a
    """
    if request.session.get(sid, '') == '':
        request.session.set_expiry(0)
        request.session[sid] = _generate_sid()
    return request.session[sid]


def _generate_sid():
    """
    Метод возвращает строку из 50 случайных символов, которая будет значением
    сессии пользователя
    """
    sid = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*() '
    sid_length = 50
    for y in range(sid_length):
        sid += characters[randint(0, len(characters)-1)]
    return sid
