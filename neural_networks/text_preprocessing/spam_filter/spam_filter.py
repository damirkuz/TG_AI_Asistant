from typing import List

from entity.SemanticMessage import SemanticMessage


def spam_filter(messages: List[SemanticMessage]) -> List[SemanticMessage]:
    """
    Фильтрует сообщения на спам, сохраняется порядок сообщений

    :param messages: Список SemanticMessage
    :return: Список SemanticMessage
    """

    return messages



