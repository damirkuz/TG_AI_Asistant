import datetime
from enum import Enum, auto

import torch.cuda

from Entity.SemanticMessage import SemanticMessage
from neural_networks.semantic_search.components.extractor.LaBSE import LaBSeSentences
from neural_networks.semantic_search.components.ranker.CrossEncoderSentences import CrossEncoderSentences
from neural_networks.semantic_search.components.text_preprocessing.aggregator import aggregator


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
    """Основной класс для семантического поиска сообщений"""

    def __init__(self, search_mode=SearchMode.HYBRID,
                 device=("cuda" if torch.cuda.is_available() else "cpu")):
        self.search_mode = search_mode
        self.device = device
        match search_mode:
            case SearchMode.SLOW:
                self.fast_model = LaBSeSentences(device)
                self.slow_model = CrossEncoderSentences()
            case SearchMode.HYBRID:
                self.fast_model = LaBSeSentences(device)
                self.slow_model = CrossEncoderSentences()
            case SearchMode.FAST:
                self.fast_model = LaBSeSentences(device)
                self.slow_model = CrossEncoderSentences()

    def get_semantic_matches(self, query: str, messages: list[SemanticMessage], k: int = 5) -> list[SemanticMessage]:
        """Ищет сообщения, семантически близкие к запросу.

                Args:
                    query (str): Поисковый запрос.
                    messages (list[SemanticMessages]): Список сообщений для поиска.
                    k (int): Количество возвращаемых результатов (по умолчанию 5).

                Returns:
                    list[SemanticMessages]: Топ-k сообщений, отсортированных по схожести.
                """
        # Выбор стратегии поиска на основе текущего режима
        match self.search_mode:
            case SearchMode.FAST:  # Только быстрая модель
                return self._fast_search(query, messages, k)
            case SearchMode.HYBRID:  # Двухэтапный поиск
                return self._hybrid_search(query, messages, k)
            case SearchMode.SLOW:  # Псевдо-режим (фактически гибридный)
                return self._slow_search(query, messages, k)

    def _fast_search(self, query: str, messages: list[SemanticMessage], k: int) -> list[SemanticMessage]:
        """Быстрый поиск только через векторную модель"""

        # Обьеденение маленьких сообщений в одно большое
        merge_messages = aggregator.merge_messages_by_time(messages)

        # Получение топ-k результатов от векторной модели
        fast_sort_messages = self.fast_model.get_semantic_matches(query, merge_messages, k)

        # Преобразование результатов в нужный формат
        sort_merge_SemanticMessages = [message[0].get_message() for message in fast_sort_messages]

        # Обратно из одного большого сообщения получаем несколько маленьких
        sort_SemanticMessages = []
        for merge_message in sort_merge_SemanticMessages:
            message = self.fast_model.get_semantic_matches(query, merge_message.get_semantic_messages(), 1)[0]
            sort_SemanticMessages.append(message)

        return [message[0].get_message() for message in sort_SemanticMessages]

    def _hybrid_search(self, query: str, messages: list[SemanticMessage], k: int) -> list[SemanticMessage]:
        """Гибридный поиск с расширенной предварительной выборкой"""
        # Этап 1: предварительный отбор кандидатов (в 10 раз больше k)
        fast_sort_messages = self.fast_model.get_semantic_matches(query, messages, min(k * 10, len(messages)))
        sort_SemanticMessages = [message[0].get_message() for message in fast_sort_messages]

        # Этап 2: точное переранжирование предвыбранных кандидатов
        ranker_sort_messages = self.slow_model.semantic_reranker(query, sort_SemanticMessages, k)
        ranker_SemanticMessage = [message[0] for message in ranker_sort_messages]

        # Возврат топ-k результатов после переранжирования
        return ranker_SemanticMessage

    def _slow_search(self, query: str, messages: list[SemanticMessage], k: int) -> list[SemanticMessage]:
        """Заглушка для 'медленного' режима (в текущей реализации совпадает с гибридным)"""
        # В текущей реализации отличается только логикой вызова
        return self._hybrid_search(query, messages, k)


# Пример использования
if __name__ == "__main__":
    messages = [SemanticMessage(123, datetime.datetime(2023, 5, 15), 1684108800, "John", 456, "Hello world!", 789)]

    documents = [
        "Привет! Как дела?",
        "Отлично! Только что закончил проект.",
        "Круто! Расскажи подробнее.",
        "Нужно было сделать чат-бота для продаж. Сделал на Python.",
        "Вау! Насколько сложная была задача?",
        "Не очень, если использовать библиотеки вроде aiogram. Все быстро получилось.",
        "Понятно. А что насчет тестирования?",
        "Тесты написал, все работает. Сейчас буду собирать фидбек от заказчика.",
        "Удачи!",
        "Спасибо! А ты чем занят?",
        "Учу новый фреймворк для фронтенда.",
        "Какой?",
        "Vue.js. Довольно интересно.",
        "Vue - хороший выбор. Легкий в освоении.",
        "Согласен. И производительность отличная.",
        "Кстати, что насчет погоды сегодня?",
        "Солнечно, но холодно. Одевайся теплее!",
        "Спасибо, учту!",
        "Как у тебя продвигается с ремонтом?",
        "Почти закончил! Осталась только покраска.",
        "Класс! Где материалы покупал?",
        "В Леруа Мерлен. Там выбор большой.",
        "Понятно. А как насчет доставки?",
        "Доставка была быстрой и бесплатной.",
        "Супер!",
        "Что будешь делать на выходных?",
        "Поеду за город, отдохну.",
        "Отличный план!",
        "А ты?",
        "Пойду в кино.",
        "Какой фильм?",
        "Новый фильм про супергероев.",
        "Звучит интересно!",
        "Да, говорят, классный сюжет.",
        "Что насчет музыки?",
        "Сейчас слушаю рок.",
        "Какой рок?",
        "Классический рок, Led Zeppelin, например.",
        "Люблю Led Zeppelin!",
        "У них классные песни.",
        "Да, согласен. А что делаешь сейчас?",
        "Пишу статью.",
        "На какую тему?",
        "Про нейронные сети.",
        "Интересно! Что именно?",
        "Об обучении моделей для семантического поиска.",
        "Понятно. Нужно будет почитать!",
        "Конечно. Кстати, как найти информацию?",
        "В OpenAI или Яндекс, думаю.",
        "Согласен. Или можно спросить у Chat GPT!",
        "Точно! Хорошая идея."
    ]

    for doc in documents:
        messages.append(SemanticMessage(123, datetime.datetime(2023, 5, 15), 1684108800, doc, 456, doc, 789))

    semantic_search = SemanticSearch(SearchMode.HYBRID)
    #print(semantic_search.get_semantic_matches("фреймворк для веб разработки", messages, 10)[0].get_text())
    for i in semantic_search.get_semantic_matches("Погода", messages, 10):
        print(i.get_text())
