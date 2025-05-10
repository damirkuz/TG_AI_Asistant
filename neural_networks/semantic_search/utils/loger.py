import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init

# Инициализация colorama (автоматически сбрасывает цвета после вывода)
init(autoreset=True)

# Создаем папку для логов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Основной логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Форматтер для файлов (без цвета)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Форматтер для консоли с синим цветом
console_formatter = logging.Formatter(
    f"{Fore.BLUE}%(asctime)s - %(name)s - %(levelname)s - %(message)s{Style.RESET_ALL}",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Обработчики
file_handler = RotatingFileHandler(LOG_DIR / "app.log", maxBytes=1024*1024, backupCount=5, encoding="utf-8")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(console_handler)