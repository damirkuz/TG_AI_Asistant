from typing import Any
from Entity.SemanticMessage import SemanticMessage


class EmbeddingMessage:
    """Класс для хранения произвольного сообщения и его векторного представления."""

    def __init__(self, message: Any, embedding: list):
        """
        Args:
            message: Сообщение любого типа.
            embedding: Векторное представление.
        """
        self._message = message
        self._embedding = embedding

    def get_message(self) -> Any:
        """Возвращает сообщение (произвольный тип)."""
        return self._message

    def set_message(self, value: Any) -> None:
        """Устанавливает сообщение (принимает любой тип)."""
        self._message = value

    def get_embedding(self) -> list:
        """Возвращает векторное представление сообщения."""
        return self._embedding

    def set_embedding(self, value: list) -> None:
        """Устанавливает эмбеддинг (список чисел)."""
        self._embedding = value
