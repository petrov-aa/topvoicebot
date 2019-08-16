"""
Бот
"""

from telebot import TeleBot, apihelper
from telebot.types import Message as TelegramMessage

from app import config, db
from app.messages import t
from app.models import Chat

if config.BOT_PROXY:
    apihelper.proxy = {"https": config.BOT_PROXY}

bot = TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=["start", "help"])
@db.commit_session
def on_help_command(message: TelegramMessage, session=None):
    chat = Chat.get_by_telegram_chat_id(message.chat.id)
    bot.send_message(chat.telegram_chat_id, t("app.message.help"), parse_mode="Markdown")
