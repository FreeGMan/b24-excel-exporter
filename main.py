import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.v1.router import router as router_v1
from app.logger import get_logger

logger = get_logger("Main")

def create_app() -> FastAPI:
    app = FastAPI(title="b24-excel-exporter")
    
    # Подключаем роутер API
    app.include_router(router_v1, prefix="/api/v1")
    
    # Монтируем папку с файлами. Теперь файлы доступны по адресу: https://host:port/files/имя_файла
    app.mount("/files", StaticFiles(directory=settings.files_dir), name="files")
    
    return app

app = create_app()

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "b24-excel-exporter"}

if __name__ == "__main__":
    logger.info(f"Starting server at https://{settings.host}:{settings.port}")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=settings.port, 
        reload=True,
        ssl_keyfile=settings.ssl_keyfile,
        ssl_certfile=settings.ssl_certfile
    )