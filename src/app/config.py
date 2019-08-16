"""
Конфигурация бота
"""

import os

from app.messages import t

# Токен бота - обязателен
ENV_VAR_BOT_TOKEN = "APP_BOT_TOKEN"
if ENV_VAR_BOT_TOKEN not in os.environ:
    raise Exception(t("app.config.bot_token_not_specified"))
BOT_TOKEN = os.environ[ENV_VAR_BOT_TOKEN]

# Прокси для бота - необязательно
ENV_VAR_BOT_PROXY = "APP_BOT_PROXY"
BOT_PROXY = os.environ[ENV_VAR_BOT_PROXY] if ENV_VAR_BOT_PROXY in os.environ else None
