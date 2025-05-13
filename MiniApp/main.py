from fastapi import FastAPI, Request
from environs import Env
#from database.db_core import async_session_maker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import hashlib
import hmac

# app = FastAPI(middleware=[Middleware(telegram_only_middleware)]) # Блокировка захода не из telegram
app = FastAPI()

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="MiniApp/static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="MiniApp/templates")

# Пример данных о чатах
chat_list = ["Общий чат", "Техподдержка", "Разработка", "Маркетинг"]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
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

@app.post("/verify")
async def verify(request: Request):
    form_data = await request.form()
    init_data = form_data.get("initData")
    print(init_data)
    if not init_data:
        raise HTTPException(status_code=400, detail="No initData provided")
    env = Env()
    env.read_env(None)
    BOT_TOKEN = env("BOT_TOKEN")
    if not validate_init_data(init_data, BOT_TOKEN):
        raise HTTPException(status_code=403, detail="Invalid initData")
    
    # Извлекаем user ID для проверки в БД
    user_id = extract_user_id(init_data)
    
    # Здесь будет проверка на существование user в бд
    user_exists = True  # Заглушка
    
    if not user_exists:
        raise HTTPException(status_code=403, detail="User not found in database")
    
    return {"status": "ok"}

def extract_user_id(init_data: str) -> str:
    """Извлекает user_id из initData"""
    params = dict(pair.split('=') for pair in init_data.split('&'))
    user_str = params.get('user', '')
    if user_str:
        import json
        user_data = json.loads(user_str)
        return str(user_data.get('id'))
    return None

def validate_init_data(init_data: str, bot_token: str) -> bool:
    pairs = init_data.split('&')
    data = {}
    for pair in pairs:
        key, value = pair.split('=')
        data[key] = value
    
    hash_str = data.pop('hash')
    data_str = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
    
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(secret_key, data_str.encode(), hashlib.sha256).hexdigest()
    
    return computed_hash == hash_str

async def telegram_only_middleware(request: Request, call_next):
    if request.url.path == "/webapp":
        if "initData" not in request.query_params:
            raise HTTPException(status_code=403)
        
        if not validate_init_data(request.query_params["initData"], "YOUR_BOT_TOKEN"):
            raise HTTPException(status_code=403)
    
    return await call_next(request)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
