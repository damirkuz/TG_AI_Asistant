import datetime

from sentence_transformers import SentenceTransformer
import faiss
from faiss import IndexFlatL2
from numpy import ndarray

from entity.SemanticMessage import SemanticMessage
from neural_networks.semantic_search.components.extractor.EmbeddingMessage import EmbeddingMessage

from neural_networks.semantic_search.utils.loger import logger


class LaBSeSentences:
    def __init__(self, device="cpu"):
        self.device = device
        self.model = SentenceTransformer("Moriec/Vinogradov_semantic_search", device=device)
        # self.model.save("local_model/")

    def get_semantic_matches(self, query: str, messages: list, k: int) -> list[[EmbeddingMessage, int]]:
        embeddings_messages = self.encode_messages(messages)
        embedding_query = self.encode_query(query)
        index = self.build_index(embeddings_messages)
        distances, indices = index.search(embedding_query, k)
        sort_messages = [
            [EmbeddingMessage(messages[idx_message], embeddings_messages[idx_message]), distances[0][idx_distances]]
            for idx_message, idx_distances in zip(indices[0], range(len(distances[0])))]
        return sort_messages[0:min(k, len(messages))]

    def encode_messages(self, messages: list) -> ndarray:
        embedding_messages = self.model.encode([message.get_text() for message in messages])
        return embedding_messages

    def encode_query(self, query: str) -> ndarray:
        embedding_query = self.model.encode([query])
        return embedding_query

    def build_index(self, embeddings: ndarray) -> IndexFlatL2:
        dimension = embeddings.shape[1]  # Размерность вектора
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        return index


if __name__ == "__main__":
    kk = LaBSeSentences()

    query = "фреймворк для веб разработки"
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

    ms = []
    for i in documents:
        ms.append(SemanticMessage(123, datetime.datetime(2023, 5, 15), 1684108800, "John", 456, i, 789))

    ans = kk.get_semantic_matches(query, ms, 15)
    print(len(ans))
    for i in ans:
        print(i[0].get_message().get_text(), i[1])
