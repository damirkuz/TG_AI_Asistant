from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import hashlib
import hmac
import logging
from environs import Env
from telethon import TelegramClient
from database.db_core import async_session_maker
from sqlalchemy import select
from typing import Optional

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения
env = Env()
env.read_env()
BOT_TOKEN = env("BOT_TOKEN")

# Инициализация клиента Redis (заглушка)
class RedisClientStorage:
    async def get_client(self, bot_user_id: int) -> TelegramClient:
        """Получение Telethon клиента из Redis"""
        # Здесь должна быть реальная реализация
        return TelegramClient(...)

redis_client_storage = RedisClientStorage()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация ресурсов при старте
    logger.info("Starting application...")
    
    # Здесь можно инициализировать соединения с БД, Redis и т.д.
    try:
        yield
    finally:
        # Очистка ресурсов при завершении
        logger.info("Shutting down application...")

app = FastAPI(lifespan=lifespan)

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="MiniApp/static"), name="static")
templates = Jinja2Templates(directory="MiniApp/templates")

# Пример данных о чатах
chat_list = ["Общий чат", "Техподдержка", "Разработка", "Маркетинг"]

# Зависимость для получения сессии БД
async def get_db():
    async with async_session_maker() as session:
        yield session

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "chat_list": chat_list,
            "title": "Анализатор чатов"
        }
    )

@app.post("/")
async def analyze_chat(request: Request):
    """Обработка формы анализа чата"""
    form_data = await request.form()
    # Здесь будет обработка формы
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "chat_list": chat_list,
            "title": "Анализатор чатов"
        }
    )

class VerifyRequest(BaseModel):
    initData: str
    initDataUnsafe: dict

@app.post("/verify")
async def verify(
    request: VerifyRequest, 
    db=Depends(get_db)
):
    # print(request.initDataUnsafe)
    """Верификация данных Telegram WebApp"""
    try:
        logger.info("Starting verification process")
        
        # Валидация initData
        # if not validate_init_data(request.initData, BOT_TOKEN):
        #     logger.warning("Invalid initData received")
        #     raise HTTPException(status_code=403, detail="Invalid initData")
        # TODO : надо переделать 
        
        # Получение user_id
        user_id = extract_user_id(request.initDataUnsafe)
        if not user_id:
            logger.warning("No user ID found in initData")
            raise HTTPException(status_code=400, detail="No user ID provided")
        if not isUserFromDB(id):
            logger.warning("No user in db")
            raise HTTPException(status_code=400, detail="No user ID provided")
        # else:
        #     print("All ok")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
async def isUserFromDB(id: int) -> bool:
    async with async_session_maker() as session:
        exists = session.query(
        session.query(bot_user).filter_by(telegram_id=id).exists()
        ).scalar()
        yield session

def extract_user_id(init_data: str) -> Optional[str]:
    """Извлекает user_id из initData"""
    try:
        
        user_str = init_data["user"]["id"]
        if user_str:
            return user_str
        return None
    except Exception as e:
        logger.error(f"Error extracting user ID: {str(e)}")
        return None

def validate_init_data(init_data: str, bot_token: str) -> bool:
    """Валидация Telegram WebApp initData"""
    try:
        pairs = init_data.split('&')
        data = {}
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                data[key] = value
        
        if 'hash' not in data:
            return False
            
        hash_str = data.pop('hash')
        data_str = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
        
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        computed_hash = hmac.new(secret_key, data_str.encode(), hashlib.sha256).hexdigest()
        
        return computed_hash == hash_str
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return False

@app.get("/dialogs/{user_id}")
async def get_dialogs(user_id: int):
    """Получение списка диалогов через Telethon"""
    try:
        tg_client = await redis_client_storage.get_client(bot_user_id=user_id)
        dialogs = []
        async for dialog in tg_client.iter_dialogs():
            dialogs.append({
                "name": dialog.name,
                "id": dialog.id,
                "unread": dialog.unread_count
            })
        return {"dialogs": dialogs}
    except Exception as e:
        logger.error(f"Error getting dialogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving dialogs")
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("MiniApp.miniapp:app", host="0.0.0.0", port=8000, reload=True)