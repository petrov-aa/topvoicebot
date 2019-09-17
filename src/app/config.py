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

# Способ запуска бота: полинг или вебхук - обязательный
ENV_VAR_RUN_METHOD = "APP_RUN_METHOD"
if ENV_VAR_RUN_METHOD not in os.environ:
    raise Exception(t("app.config.run_method_not_specified"))
RUN_METHOD = os.environ[ENV_VAR_RUN_METHOD]

# Путь к файлу логов - обязательный
ENV_VAR_LOG_FILENAME = "APP_LOG_FILENAME"
if ENV_VAR_LOG_FILENAME not in os.environ:
    raise Exception(t("app.config.log_filename_not_specified"))
LOG_FILENAME = os.environ[ENV_VAR_LOG_FILENAME]
