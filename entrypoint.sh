#!/bin/sh

# Ждем старта mysql
sleep 10

# Производим миграции
alembic upgrade head
# Запускаем приложение
python bot.py
