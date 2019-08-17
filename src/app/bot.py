"""
Бот
"""

from sqlalchemy.orm import Session
from telebot import TeleBot, apihelper
from telebot.types import Message as TelegramMessage, Chat as TelegramChat, InlineQueryResultCachedVoice

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


@bot.message_handler(commands=["cancel"])
@db.commit_session
def on_cancel_command(message: TelegramMessage, session: Session = None):
    chat = repo.chat_get_by_telegram_id(message.chat.id)
    if chat.state == Chat.STATE_WAIT_TITLE:
        data = chat.get_state_data()
        if "voice_id" not in data or data["voice_id"] is None:
            raise Exception(t("app.error.state_wait_title.no_voice_id"))
        voice_id = data["voice_id"]
        voice = repo.get_voice_by_id(voice_id)
        session.delete(voice)
        chat.clear_state()
        bot.send_message(message.chat.id, t("app.message.operation_cancelled"))


def get_channel():
    """
    Получить канал с топ войсами

    :return: Канал с топ войсами
    :rtype: TelegramChat
    """
    channel = bot.get_chat(config.CHANNEL_ID)
    if channel is None:
        raise Exception(t("app.error.channel.not_found"))
    return channel


def publish_to_channel(voice):
    channel = get_channel()
    post_message = bot.send_voice(channel.id, voice.file_id)
    title_message = bot.send_message(channel.id,
                                     voice.title,
                                     reply_to_message_id=post_message.message_id,
                                     disable_web_page_preview=True,
                                     parse_mode="Markdown")
    voice.post_message_id = post_message.message_id
    voice.title_message_id = title_message.message_id


def unpublish_from_channel(voice):
    if voice.post_message_id is None:
        raise Exception(t("app.error.channel.voice_not_published"))
    channel = get_channel()
    bot.delete_message(channel.id, voice.post_message_id)
    bot.delete_message(channel.id, voice.title_message_id)


@bot.message_handler(commands=["publish"])
@db.commit_session
def on_publish_command(message: TelegramMessage, session: Session = None):
    chat = repo.chat_get_by_telegram_id(message.chat.id)
    if chat.state is None:
        if message.reply_to_message is None:
            return
        if message.reply_to_message.voice is None:
            return
        file_id = message.reply_to_message.voice.file_id
        voice = repo.get_voice_by_file_id(file_id)
        if voice is None or not voice.is_active():
            bot.send_message(message.chat.id, t("app.error.voice.voice_not_found"))
            return
        if not voice.can_edit(chat):
            bot.send_message(message.chat.id, t("app.error.voice.no_access"))
            return
        if voice.is_public:
            bot.send_message(message.chat.id, t("app.error.voice.already_published"))
            return
        voice.is_public = True
        publish_to_channel(voice)
        bot.send_message(message.chat.id, t("app.message.voice_published"))


@bot.message_handler(commands=["unpublish"])
@db.commit_session
def on_publish_command(message: TelegramMessage, session: Session = None):
    chat = repo.chat_get_by_telegram_id(message.chat.id)
    if chat.state is None:
        if message.reply_to_message is None:
            return
        if message.reply_to_message.voice is None:
            return
        file_id = message.reply_to_message.voice.file_id
        voice = repo.get_voice_by_file_id(file_id)
        if voice is None or not voice.is_active():
            bot.send_message(message.chat.id, t("app.error.voice.voice_not_found"))
            return
        if not voice.can_edit(chat):
            bot.send_message(message.chat.id, t("app.error.voice.no_access"))
            return
        if not voice.is_public:
            bot.send_message(message.chat.id, t("app.error.voice.not_published"))
            return
        voice.is_public = False
        unpublish_from_channel(voice)
        bot.send_message(message.chat.id, t("app.message.voice_unpublished"))


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
        file_id = message.voice.file_id
        # Проверяем был ли войс добавлен ранее. Уникальность войса определяется по file_id
        # TODO проверять уникальность войса по file_id и id пользователя, чтобы
        # можно было добавлять один и тот же войс разным пользователями без публикации
        check_voice = repo.get_voice_by_file_id(file_id)
        if check_voice is not None:
            bot.send_message(message.chat.id, t("app.error.voice.voice_already_exists"))
            return
        voice = Voice()
        voice.file_id = file_id
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
        # Устанавливаем состояние войса в новый, чтобы он пока был недоступен в поиске
        voice.status = Voice.STATUS_NEW
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
        voice.search_title = utils.create_search_title(voice.title)
        # Помечаем войс как активный
        voice.status = Voice.STATUS_ACTIVE
        chat.clear_state()
        bot.send_message(message.chat.id, t("app.message.voice_successfully_saved"))


def build_suggestions_on_query(query: str, chat_id: int):
    suggestions = list()
    if len(query) > 0:
        voices = repo.search_voice(query, chat_id)
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
    search_query_text = utils.create_search_title(query_text)
    suggestions = list()
    if len(search_query_text) > 0:
        chat = repo.chat_get_by_telegram_id(query.from_user.id)
        suggestions = build_suggestions_on_query(query_text, chat.id)
    a = 1
    # Обязательно устанавливаем is_personal в True, чтобы личные войсы
    # не попадали к другим пользователям
    # Кеш полностью отключаем
    bot.answer_inline_query(query.id,
                            suggestions,
                            cache_time=0,
                            is_personal=True)
