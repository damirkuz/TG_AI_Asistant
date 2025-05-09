import datetime

from faiss import IndexFlatL2
from numpy import ndarray
from sentence_transformers import SentenceTransformer
import faiss

from Entity.SemanticMessage import SemanticMessage
from neural_networks.semantic_search.components.extractor.EmbeddingMessage import EmbeddingMessage


class LaBSeSentences:
    def __init__(self, device="cpu"):
        self.device = device
        self.model = SentenceTransformer('sentence-transformers/LaBSE', device=device)
        #self.model.save("local_model/")

    def get_semantic_matches(self, query: str, messages: list, k: int) -> list[[EmbeddingMessage, int]]:
        embeddings_messages = self.encode_messages(messages)
        embedding_query = self.encode_query(query)
        index = self.build_index(embeddings_messages)
        distances, indices = index.search(embedding_query, k)
        print(distances[0])
        sort_messages = [
            [EmbeddingMessage(messages[idx_message], embeddings_messages[idx_message]), distances[0][idx_distances]]
            for idx_message, idx_distances in zip(indices[0], range(len(distances[0])))]
        return sort_messages[0:min(k, len(sort_messages))]

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
    ll = [SemanticMessage(123, datetime.datetime(2023, 5, 15), 1684108800, "John", 456, "Это кошка", 789),
          SemanticMessage(123, datetime.datetime(2023, 5, 15), 1684108800, "John", 456, "Это собака", 789)]
    query = "Мяу"
    ans = kk.get_semantic_matches(query, ll, 2)
    print(len(ans))
    for i in ans:
        print(i[0].get_message().get_text(), i[1])
