"""
Бот
"""

from telebot import TeleBot, apihelper
from telebot.types import Message as TelegramMessage

from app import config
from app.messages import t

if config.BOT_PROXY:
    apihelper.proxy = {"https": config.BOT_PROXY}

bot = TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=["start", "help"])
def on_help_command(message: TelegramMessage):
    bot.send_message(message.chat.id, t("app.message.help"), parse_mode="Markdown")
