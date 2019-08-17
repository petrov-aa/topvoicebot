"""
Бот
"""

from telebot import TeleBot, apihelper
from telebot.types import Message as TelegramMessage, InlineQueryResultVoice, InlineQueryResultCachedVoice

from app import config, db, repo, utils
from app.models import Chat, Voice
from app.messages import t

if config.BOT_PROXY:
    apihelper.proxy = {"https": config.BOT_PROXY}

bot = TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=["start", "help"])
@db.commit_session
def on_help_command(message: TelegramMessage, session=None):
    chat = repo.chat_get_by_telegram_id(message.chat.id)
    bot.send_message(chat.telegram_chat_id, t("app.message.help"), parse_mode="Markdown")


def deduct_voice_author(message: TelegramMessage):
    """
    Возвращает идентификатор в телеграм автора войса. Войс может быть переслан
    или записан в чате с ботом. В первом случае вернется идентификатор пользователя,
    от которого был переслан войс, а во втором идентификатор отправителя.
    :param message: Объект сообщения из telebot
    :return: Идентификатор автора войса в телеграм
    """
    if message.forward_from is not None:
        return message.forward_from.id
    if message.forward_from_chat is not None:
        return message.forward_from_chat.id
    return message.from_user.id


@bot.message_handler(content_types=["voice"])
@db.commit_session
def on_voice(message: TelegramMessage, session=None):
    """
    Бот получает войс.

    Сценарии:

    1) Пользователь записывает новый войс в чате с ботом. При этом
    состояние чата должно быть пустым. После получения войса, бот
    сохраняет войс в базе и предлагает пользователю отправить название
    для войса.

    :param message: Сообщение телеграм с войсом
    :param session: Сессия БД
    :return:
    """
    chat = repo.chat_get_by_telegram_id(message.chat.id)
    if chat.state is None:
        # Состояние чата пусто, сохраняем войс как новый
        voice = Voice()
        voice.file_id = message.voice.file_id
        voice.sender = chat
        author_id = deduct_voice_author(message)
        author = bot.get_chat(author_id)
        voice.author_id = author_id
        # Если у автора сообщения нет ни имени ни фамилии, то
        # считаем его пересланным от канала или бота - в этом
        # случае просто игнорируем войс
        if author.first_name is None and author.last_name is None:
            return
        voice.author_first_name = author.first_name
        voice.author_last_name = author.last_name
        session.add(voice)
        session.flush()
        chat.set_state_wait_title(voice.id)
        bot.send_message(message.chat.id, t("app.message.send_title"))


@bot.message_handler(content_types=["text"])
@db.commit_session
def on_text(message: TelegramMessage, session=None):
    """
    Бот получает текст.

    Сценарии:

    1) Пользователь записывает новый войс в чате с ботом. Бот уже получил войс и предложил
    пользователю ввести название войса. При этом состояние чата `STATE_WAIT_TITLE`. После
    получения фразы, бот записывает название в войс и отправляет сообщение, что войс
    успешно добавлен

    :param message: Сообщение телеграм
    :param session: Сессия БД
    :return:
    """
    chat = repo.chat_get_by_telegram_id(message.chat.id)
    if chat.state == Chat.STATE_WAIT_TITLE:
        state_data = chat.get_state_data()
        if state_data is None or "voice_id" not in state_data or state_data["voice_id"] is None:
            return
        if len(message.text) == 0:
            return
        voice_id = state_data["voice_id"]
        voice = repo.get_voice_by_id(voice_id)
        voice.title = message.text
        chat.state = None
        bot.send_message(message.chat.id, t("app.message.voice_successfully_saved"))


def build_suggestions_on_query(query: str):
    suggestions = list()
    if len(query) > 0:
        voices = repo.search_voice(query)
        for voice in voices:
            author_full_name = utils.voice_author_full_name(voice)
            title = "{} - {}".format(author_full_name, voice.title)
            suggestions.append(InlineQueryResultCachedVoice("{} {}".format(voice.id, voice.title),
                                                            voice.file_id,
                                                            title,
                                                            # по какой-то причине телеграм
                                                            # отвергает значение None здесь, которое по умолчанию
                                                            # Похоже на ошибку в telebot
                                                            parse_mode="Markdown"))
    return suggestions


@bot.inline_handler(lambda query: True)
@db.commit_session
def on_inline(query, session=None):
    query_text = query.query
    suggestions = build_suggestions_on_query(query_text)
    # Обязательно устанавливаем is_personal в True, чтобы личные войсы
    # не попадали к другим пользователям
    # Кеш полностью отключаем
    bot.answer_inline_query(query.id,
                            suggestions,
                            cache_time=0,
                            is_personal=True)
