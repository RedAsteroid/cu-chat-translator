from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI
from openai_llm import OpenaiLlm
from pathlib import Path
from contextlib import asynccontextmanager
import sys
from loguru import logger
from settings import api_key, base_url, model_name, port as config_port

logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    colorize=True,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} - {level: <8} - {message}"
)

missing = [
    name
    for name, value in (("model_name", model_name), ("base_url", base_url), ("api_key", api_key))
    if not str(value or "").strip()
]

if missing:
    print("=" * 46)
    print("  翻译服务无法启动")
    print("  config.yaml 中以下必填项尚未填写：" + "、".join(missing))
    print("  请填写后重新运行 run.bat。")
    print("=" * 46)
    raise SystemExit(1)

DEFAULT_PORT = 8000


def resolve_port(value) -> int:
    """读取 config.yaml 的 port；缺失或非法时回退到 8000。"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return DEFAULT_PORT
    try:
        port = int(str(value).strip())
    except (TypeError, ValueError):
        logger.warning(f"config.yaml 中 port 不是合法整数（{value!r}），已回退到 {DEFAULT_PORT}")
        return DEFAULT_PORT
    if not 1 <= port <= 65535:
        logger.warning(f"config.yaml 中 port 超出 1~65535（{port}），已回退到 {DEFAULT_PORT}")
        return DEFAULT_PORT
    return port


PORT = resolve_port(config_port)

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s | %(levelname)s | %(message)s"}},
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "formatter": "plain",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "uvicorn": {"handlers": ["stderr"], "level": "WARNING", "propagate": False},
        "uvicorn.error": {"handlers": ["stderr"], "level": "WARNING", "propagate": False},
        "uvicorn.access": {"handlers": ["stderr"], "level": "WARNING", "propagate": False},
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.success(f"服务已就绪：http://0.0.0.0:{PORT}")
    yield
    logger.info("服务已停止")


app = FastAPI(lifespan=lifespan)
client = AsyncOpenAI(
    api_key=api_key,
    base_url=base_url
)


def read_prompt_file(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        return [{"role": "system", "content": content.strip()}]


system_messages = read_prompt_file(
    file_path=Path(__file__).parent / "prompt.txt"
)


async def do_translate(text: str, source: str, target: str) -> str:
    logger.info(f"翻译: {source} → {target}, 文本: {text}")
    openai_service = OpenaiLlm(
        system_messages=system_messages,
        model_name=model_name,
        client=client
    )
    result = await openai_service.call_openai_json_api(
        user_message=text,
        source_lang=source,
        target_lang=target
    )
    logger.success(f"翻译完成: {result}")
    return result["translatedText"]


@app.post("/")
async def translate_root(request: Request):
    try:
        body = await request.json()
        logger.info(f"收到请求(根路径): {body}")
        text = body.get("q")
        source = body.get("source", "auto")
        target = body.get("target", "zh")
        if not text:
            raise HTTPException(status_code=400, detail="Missing q field")
        translated = await do_translate(text, source, target)
        return JSONResponse(content={"translatedText": translated})
    except Exception as e:
        logger.error(f"处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate")
async def translate_standard(request: Request):
    try:
        body = await request.json()
        logger.info(f"收到请求(/translate): {body}")
        text = body.get("q")
        source = body.get("source", "auto")
        target = body.get("target", "zh")
        if not text:
            raise HTTPException(status_code=400, detail="Missing q field")
        translated = await do_translate(text, source, target)
        return JSONResponse(content={"translatedText": translated})
    except Exception as e:
        logger.error(f"处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"正在启动翻译服务，端口 {PORT}")
    logger.info(f"热重载监视目录：{Path(__file__).parent}")
    logger.info("按 Ctrl+C 停止服务")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_config=LOG_CONFIG
    )