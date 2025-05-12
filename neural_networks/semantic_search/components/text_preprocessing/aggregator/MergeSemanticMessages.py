from Entity.SemanticMessage import SemanticMessage


class MergeSemanticMessages:
    def __init__(self, semantic_messages: list[SemanticMessage]):
        self.semantic_messages = semantic_messages
        self.text = ''
        for semantic_message in semantic_messages:
            self.text += " " + semantic_message.get_text()

    def get_text(self):
        return self.text

    def get_semantic_messages(self):
        return self.semantic_messages
