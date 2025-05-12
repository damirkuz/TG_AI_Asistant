from sentence_transformers import CrossEncoder

model_name = 'cointegrated/rubert-base-cased-nli-stsb'  # Используйте эту модель
model = CrossEncoder(model_name)

sentences = ["Как дела?", "Что нового?", "Как жизнь?", "Что случилось?"]

# Пример использования
scores = model.predict([("Как дела?", "Что нового?"),
                       ("Как дела?", "Как жизнь?"),
                       ("Как дела?", "Что случилось?")])

print(scores)  # Вероятности семантической близости

# Пример поиска наиболее похожего запроса:
query = "Как ты поживаешь?"
corpus = ["Как дела?", "Что нового?", "Как жизнь?", "Что случилось?"]

pairs = [(query, doc) for doc in corpus]
scores = model.predict(pairs)

best_index = scores.argmax()
most_similar = corpus[best_index]

print(f"Запрос: {query}")
print(f"Наиболее похожий запрос: {most_similar}")
print(f"Оценка близости: {scores[best_index]}")