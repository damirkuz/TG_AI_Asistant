import datetime
from enum import Enum, auto

from Entity.SemanticMessage import SemanticMessage
from neural_networks.semantic_search.components.extractor.LaBSE import LaBSeSentences


class SearchMode(Enum):
    """Режимы работы семантического поиска.

       Attributes:
           FAST: Быстрый, но менее точный поиск (приближенные методы).
           SLOW: Медленный, но точный поиск (полный перебор).
           HYBRID: Комбинированный подход: FAST-фильтрация + SLOW-уточнение.
       """
    FAST = auto()
    SLOW = auto()
    HYBRID = auto()


class SemanticSearch:
    """Поиск сообщений, семантически близких к запросу.

        Args:
            search_mode (SearchMode): Режим работы (по умолчанию HYBRID).

        Methods:
            get_semantic_matches: Возвращает топ-k сообщений, схожих с запросом.
        """

    def __init__(self, search_mode=SearchMode.HYBRID, ):
        self.search_mode = search_mode

    def get_semantic_matches(self, query: str, messages: list[SemanticMessage], k: int = 5) -> list[SemanticMessage]:
        """Ищет сообщения, семантически близкие к запросу.

                Args:
                    query (str): Поисковый запрос.
                    messages (list[SemanticMessages]): Список сообщений для поиска.
                    k (int): Количество возвращаемых результатов (по умолчанию 5).

                Returns:
                    list[SemanticMessages]: Топ-k сообщений, отсортированных по схожести.
                """
        fast_model = LaBSeSentences()
        fast_sort_messages = fast_model.get_semantic_matches(query, messages, k)
        answer = [message[0].get_message() for message in fast_sort_messages]

        return answer


# Пример использования
if __name__ == "__main__":
    messages = [SemanticMessage(123, datetime.datetime(2023, 5, 15), 1684108800, "John", 456, "Hello world!", 789)]

    semantic_search = SemanticSearch(SearchMode.SLOW)
    print(semantic_search.get_semantic_matches("Запрос", messages, 1)[0].get_text())
