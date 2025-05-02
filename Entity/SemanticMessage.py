import datetime
import time

class SemanticMessage:
    """
    Класс для представления сообщения в Telegram.
    """

    def __init__(self, message_id: int, date: datetime.datetime, date_unixtime: int, from_user: str, from_user_id: int, text: str, reply_to_message_id: int = -1):
        """
        :param message_id: Уникальный идентификатор сообщения.
        :param date: Дата и время отправки сообщения.
        :param date_unixtime: Дата и время отправки сообщения в формате Unix time.
        :param from_user: Имя отправителя.
        :param from_user_id: ID отправителя.
        :param text: Текст сообщения.
        :param reply_to_message_id: ID сообщения, на которое это сообщение отвечает (или -1).
        """
        self._id = message_id
        self._date = date
        self._date_unixtime = date_unixtime
        self._from = from_user
        self._from_id = from_user_id
        self._text = text
        self._reply_to_message_id = reply_to_message_id

    def get_id(self):
        return self._id

    def get_date(self):
        return self._date

    def get_date_unixtime(self):
        return self._date_unixtime

    def get_from(self):
        return self._from

    def get_from_id(self):
        return self._from_id

    def get_text(self):
        return self._text

    def get_reply_to_message_id(self):
        return self._reply_to_message_id

    def set_id(self, message_id: int):
        self._id = message_id

    def set_date(self, date: datetime.datetime):
        self._date = date

    def set_date_unixtime(self, date_unixtime: int):
        self._date_unixtime = date_unixtime

    def set_from(self, from_user: str):
        self._from = from_user

    def set_from_id(self, from_user_id: int):
        self._from_id = from_user_id

    def set_text(self, text: str):
        self._text = text

    def set_reply_to_message_id(self, reply_to_message_id: int):
        self._reply_to_message_id = reply_to_message_id


