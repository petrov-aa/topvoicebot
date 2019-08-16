from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from app import db

Base = declarative_base()


class Chat(Base):
    """
    Объект чата. Смысл чата в том, чтобы хранить в нем состояние чата пользователя с ботом.
    """
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    telegram_chat_id = Column(String(32), index=True, unique=True)

    @staticmethod
    @db.flush_session
    def get_by_telegram_chat_id(telegram_chat_id: int, session=None) -> "Chat":
        """
        Получить чат по идентификатору чата в телеграме. Если чата еще нет в базе, создается новый

        :param telegram_chat_id Идентификатор чата в телеграме
        :param session Сессия БД
        :return: Объект чата
        """
        chat = session.query(Chat).\
            filter(Chat.telegram_chat_id == telegram_chat_id).first()
        if chat is None:
            chat = Chat.create_new(telegram_chat_id)
        return chat

    @staticmethod
    @db.flush_session
    def create_new(telegram_chat_id: int, session=None) -> "Chat":
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
