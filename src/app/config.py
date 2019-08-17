"""
Конфигурация бота
"""

import os

from app.messages import t

# Токен бота - обязательный
ENV_VAR_BOT_TOKEN = "APP_BOT_TOKEN"
if ENV_VAR_BOT_TOKEN not in os.environ:
    raise Exception(t("app.config.bot_token_not_specified"))
BOT_TOKEN = os.environ[ENV_VAR_BOT_TOKEN]

# Прокси для бота - необязательный
ENV_VAR_BOT_PROXY = "APP_BOT_PROXY"
BOT_PROXY = os.environ[ENV_VAR_BOT_PROXY] if ENV_VAR_BOT_PROXY in os.environ else None

# URL для доступа к БД - обязательный
ENV_VAR_DB_URL = "APP_DB_URL"
if ENV_VAR_DB_URL not in os.environ:
    raise Exception(t("app.config.db_url_not_specified"))
DB_URL = os.environ[ENV_VAR_DB_URL]

# Идентификатор канала топ войсы - обязательный
ENV_VAR_CHANNEL_ID = "APP_CHANNEL_ID"
if ENV_VAR_CHANNEL_ID not in os.environ:
    raise Exception(t("app.config.channel_id_not_specified"))
CHANNEL_ID = os.environ[ENV_VAR_CHANNEL_ID]
