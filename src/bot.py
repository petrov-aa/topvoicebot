from app.bot import bot

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True, timeout=9999)
