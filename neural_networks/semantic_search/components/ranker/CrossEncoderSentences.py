from sentence_transformers import CrossEncoder

from entity.SemanticMessage import SemanticMessage


class CrossEncoderSentences:
    """
    Класс для семантического ранжирования текстов с использованием CrossEncoder.

    Attributes:
        device (str): Устройство для вычислений (cpu/cuda)
        reranker_model (CrossEncoder): Модель для ранжирования текстов
    """

    def __init__(self, device="cpu"):
        self.device = device

        # Загрузка предобученной модели для русского языка
        self.reranker_model = CrossEncoder('DiTy/cross-encoder-russian-msmarco',
                                           max_length=512, device=device)

    def semantic_reranker(self, query: str, messages: list[SemanticMessage], k: int) -> list[SemanticMessage, int]:
        """
            Ранжирует сообщения по релевантности запросу и возвращает топ-k результатов.

            Args:
                query: Поисковый запрос
                messages: Список сообщений для ранжирования
                k: Количество возвращаемых топ-результатов

            Returns:
                Список вида [сообщение, оценка релевантности]
        """
        # Ранжируем тексты относительно запроса
        rank_results = self.reranker_model.rank(query,
                                                [message.get_text() for message in messages])

        # Формируем результаты с оригинальными сообщениями и оценками
        rank_messages = []
        for rank_result in rank_results:
            index_message = rank_result["corpus_id"]  # Индекс сообщения в списке
            score = rank_result["score"]  # Оценка релевантности
            rank_messages.append([messages[index_message], score])

        # Возвращаем первые k результатов
        return rank_messages[0:k]
