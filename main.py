import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from datetime import datetime
from typing import List, Dict, Any
import dotenv
from dto import (
    KeyboardRequest, KeyboardResponse, KeyboardRequestUpdate,
    Message, EnterKeyboard, Image, ImageURL, Command,
    ActionOnMessage, Error, SendPlaceInfoRequest, SendPlaceInfoResponse,
    SendPlaceInfoRequestWithMessage, Button, EnterButtonKeyboard
)

# Configuration
dotenv.load_dotenv('.env')

LOG_STORAGE: List[Dict[str, Any]] = []  # In-memory storage for logs
BACKEND_URL = os.environ['BACKEND_URL']  # Target backend for forwarding

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="A bot for collecting feedback and monitoring service levels API",
    version="0.0.1",
    servers=[{"url": "http://localhost:8080/", "description": "Dev server"}],
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Helper functions
def log_request(endpoint: str, method: str, payload: Dict[str, Any], tag: str):
    """Log incoming request to in-memory storage."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "method": method,
        "payload": payload,
        "tag": tag
    }
    LOG_STORAGE.append(log_entry)
    logger.info(f"Logged {tag} request to {endpoint}: {payload}")

async def forward_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Forward request to backend and return response."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{BACKEND_URL}{endpoint}"
            headers = {"X-Connector-Name": "mock"}
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Backend returned error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to backend: {e}")
            raise HTTPException(status_code=502, detail=f"Backend unavailable: {str(e)}")

# Root endpoint to display logs
@app.get("/")
async def get_logs():
    """Display all logged requests."""
    return {
        "logs": LOG_STORAGE,
        "count": len(LOG_STORAGE)
    }

# API's модуля (Модуль вызывает api коннектора) - Log only
@app.post("/keyboard/create", response_model=KeyboardResponse)
async def send_keyboard(request: KeyboardRequest):
    """Метод отправки клавиатуры"""
    log_request("/keyboard/create", "POST", request.dict(), "API's модуля")
    # For module APIs, we just log and return a mock response
    return KeyboardResponse(
        user_id=request.user_id,
        place=SendPlaceInfoResponse(
            chat_id=request.place.chat_id,
            message_id="mock_message_id"
        ),
        date_time=datetime.now().isoformat()
    )

@app.post("/keyboard/update")
async def update_keyboard(request: KeyboardRequestUpdate):
    """Метод обновления клавиатуры"""
    log_request("/keyboard/update", "POST", request.dict(), "API's модуля")
    return {"status": "success", "message": "Keyboard updated (logged)"}

@app.post("/message")
async def send_message(request: Message):
    """Метод отправки сообщения"""
    log_request("/message", "POST", request.dict(), "API's модуля")
    # Return mock response matching OpenAPI spec
    return SendPlaceInfoRequestWithMessage(
        user_id=request.user_id,
        place=SendPlaceInfoResponse(
            chat_id=request.place.chat_id,
            message_id="mock_message_id"
        ),
        date_time=datetime.now().isoformat()
    )

# API's коннектора (Коннектор вызывает api модуля) - Forward to backend
@app.post("/keyboard/input")
async def enter_keyboard(request: EnterKeyboard):
    """Метод отправки выбранной кнопки"""
    log_request("/keyboard/input", "POST", request.dict(), "API's коннектора")
    response = await forward_request("/keyboard/input", request.dict())
    return response

@app.post("/image", response_model=ImageURL)
async def send_images(request: Image):
    """Метод отправки изображений"""
    log_request("/image", "POST", request.dict(), "API's коннектора")
    response = await forward_request("/image", request.dict())
    return ImageURL(**response)

@app.post("/command")
async def send_command(request: Command):
    """Метод отправки команды"""
    log_request("/command", "POST", request.dict(), "API's коннектора")
    response = await forward_request("/command", request.dict())
    return response

@app.post("/user_message")
async def send_message_from_module(request: Message):
    """Метод отправки сообщения от пользователя"""
    log_request("/user_message", "POST", request.dict(), "API's коннектора")
    response = await forward_request("/user_message", request.dict())
    return response

@app.post("/message/action")
async def send_action_on_message(request: ActionOnMessage):
    """Метод отправки действия над сообщением"""
    log_request("/message/action", "POST", request.dict(), "API's коннектора")
    response = await forward_request("/message/action", request.dict())
    return response

# API's модуля агента
@app.post("/appeal-agent")
async def start_appeal_processing(request: Dict[str, Any]):
    """Отправить обращение агенту"""
    log_request("/appeal-agent", "POST", request, "API's модуля агента")
    # For now, just log and return mock response
    return {
        "Result": {
            "Описание проблемы": "Mock response",
            "Классификация": {
                "Категория": "ТехПоддержка",
                "ПО": "ККМ",
                "Критичность": "проблема",
                "Эскалация": True
            }
        },
        "chatId": 12321
    }

# Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=Error(code=exc.status_code, message=str(exc.detail)).dict()
    )

if __name__ == "__main__":
    import uvicorn
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    uvicorn.run(app, host="0.0.0.0", port=8080)
