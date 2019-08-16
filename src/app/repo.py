"""
Интерфейс взаимодействия с объектами в базе данных
"""

from app import db
from app.models import Chat


@db.flush_session
def chat_get_by_telegram_id(telegram_chat_id: int, session=None) -> Chat:
    """
    Получить чат по идентификатору чата в телеграме. Если чата еще нет в базе, создается новый

    :param telegram_chat_id Идентификатор чата в телеграме
    :param session Сессия БД
    :return: Объект чата
    """
    chat = session.query(Chat).\
        filter(Chat.telegram_chat_id == telegram_chat_id).first()
    if chat is None:
        chat = chat_create_new(telegram_chat_id)
    return chat


@db.flush_session
def chat_create_new(telegram_chat_id: int, session=None) -> Chat:
    """
    Создает новый чат

    :param telegram_chat_id: Идентификатор чата в телеграме
    :param session: Сессия БД
    :return: Созданный чат
    """
    chat = Chat()
    chat.telegram_chat_id = telegram_chat_id
    session.add(chat)
    session.flush()
    return chat
