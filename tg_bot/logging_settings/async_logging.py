import logging
import logging.handlers
import queue

# Очередь для логов
log_queue = queue.Queue(-1)

format = ('[%(asctime)s] #%(levelname)-8s %(filename)s:'
          '%(lineno)d - %(name)s:%(funcName)s - %(message)s')

# Обработчик, который кладёт логи в очередь
queue_handler = logging.handlers.QueueHandler(log_queue)

# Обычный обработчик (например, файл + консоль)
file_handler = logging.handlers.RotatingFileHandler(
    "app.log", maxBytes=10 * 1024 * 1024, backupCount=5
)
file_handler.setFormatter(logging.Formatter(format))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(format))

# QueueListener - слушатель, который пишет логи из очереди в обработчики
listener = logging.handlers.QueueListener(log_queue, file_handler, console_handler)


def setup_async_logging(level=logging.INFO):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [queue_handler]
    listener.start()
