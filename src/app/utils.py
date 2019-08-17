"""
Вспомогательные функции
"""

import re

from app.models import Voice


def voice_author_full_name(voice: Voice):
    """
    Полное имя автора войса

    :param voice: Объект класса Voice
    :return: Полное имя автора
    """
    def name_part_filter(item):
        return item is not None
    name_parts = filter(name_part_filter, [voice.author_first_name, voice.author_last_name])
    return " ".join(name_parts)


def create_search_title(title: str):
    title = title.lower()
    chars = list(title)

    def char_filter(char):
        return re.match(r"[А-яЁёA-z0-9]", char)

    filtered = filter(char_filter, chars)

    return "".join(filtered)
