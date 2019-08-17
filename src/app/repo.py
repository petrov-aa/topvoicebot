"""
Интерфейс взаимодействия с объектами в базе данных
"""
from sqlalchemy import or_, true
from sqlalchemy.orm import Session

from app import db
from app.models import Chat, Voice


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


@db.flush_session
def get_voice_by_id(voice_id: int, session=None) -> Voice:
    """
    Возвращает войс по идентификатору войса

    :param voice_id: Идентификатор войса
    :param session: Сессия БД
    :return: Войс или None
    """
    return session.query(Voice)\
        .filter(Voice.id == voice_id)\
        .first()


@db.flush_session
def get_voice_by_file_id(file_id: str, session=None) -> Voice:
    """
    Возвращает войс по идентификатору файла в телеграме

    :param file_id: Идентификатор файла войса в телеграме
    :param session: Сессия БД
    :return: Войс или None
    """
    return session.query(Voice)\
        .filter(Voice.file_id == file_id)\
        .first()


@db.flush_session
def search_voice(query: str, chat_id: int, session: Session = None) -> list:
    search = "%{}%".format(query)
    return session.query(Voice)\
        .filter(Voice.status == Voice.STATUS_ACTIVE)\
        .filter(or_(Voice.is_public == true(), Voice.sender_id == chat_id))\
        .filter(Voice.search_title.like(search))\
        .all()
