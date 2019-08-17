"""
Вспомогательные функции
"""

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
