import json

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Chat(Base):
    """
    Объект чата. Смысл чата в том, чтобы хранить в нем состояние чата пользователя с ботом.
    """
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    telegram_chat_id = Column(String(32), index=True, unique=True)
    # Состояние чата пользователя с ботом
    state = Column(String(255))
    # Данные для состояния в формате JSON
    data = Column(Text)

    STATE_WAIT_TITLE = "wait_title"

    def set_state_wait_title(self, voice_id):
        """
        Устанавливает состояние чата в состояние ожидания названия для войса

        :param voice_id: Идентификатор войса
        """
        data = {"voice_id": voice_id}
        self.state = self.STATE_WAIT_TITLE
        self.data = json.dumps(data)

    def clear_state(self):
        """
        Очищает состояние чата

        """
        self.state = None
        self.data = None

    def get_state_data(self):
        """
        Данные состояния чата

        :return: dict состояния чата
        """
        if self.state is None:
            return None
        if self.data is None:
            return None
        return json.loads(self.data)


class Voice(Base):
    """
    Войс.
    """
    __tablename__ = 'voice'
    id = Column(Integer, primary_key=True)
    file_id = Column(String(255))
    # Идентификатор телеграм автора войса
    author_id = Column(String(32))
    # Имя и фамилия отправителя войса. Кешируем, чтобы не ходить за каждым автором в телеграм
    author_first_name = Column(String(255))
    author_last_name = Column(String(255))
    # Идентификатор отправителя в бота
    sender_id = Column(Integer, ForeignKey("chat.id", ondelete="CASCADE"))
    sender = relationship("Chat")
    title = Column(String(255))
