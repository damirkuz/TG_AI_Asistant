import datetime

from Entity.SemanticMessage import SemanticMessage
from neural_networks. semantic_search. components. text_preprocessing. aggregator. MergeSemanticMessages import MergeSemanticMessages


def merge_messages_by_time(messages: list[SemanticMessage], time: int = 120) -> list[MergeSemanticMessages]:
    merge_messages = []
    local_messages = []
    for message in messages:
        if len(local_messages) == 0:
            local_messages.append(message)
        else:
            if compare(message, local_messages[-1], time):
                local_messages.append(message)
            else:
                merge_messages.append(MergeSemanticMessages(local_messages))
                local_messages = []
    if len(local_messages) != 0:
        merge_messages.append(MergeSemanticMessages(local_messages))
    return merge_messages


def compare(message1: SemanticMessage, message2: SemanticMessage, time: int = 120) -> bool:
    return message1.get_from() == message2.get_from() and abs(
        message1.get_date_unixtime() - message2.get_date_unixtime() <= time)


# Пример использования
if __name__ == "__main__":
    messages = []
    docs = ["Hi", "I", "am", "John"]
    for doc in docs:
        messages.append(SemanticMessage(123, datetime.datetime(2023, 5, 15), 1684108800, "John", 456, doc, 789))
    for merge_message in merge_messages_by_time(messages):
        print(merge_message.get_text())