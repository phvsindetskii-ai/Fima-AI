import asyncio

from fastapi import FastAPI
import uvicorn

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import BOT_TOKEN
from app.database.database import database
from app.handlers.start import start
from app.handlers.help import help_command
from app.handlers.chat import chat


app = FastAPI()


telegram = (
    Application.builder()
    .token(BOT_TOKEN)
    .build()
)


async def post_init():
    await database.initialize()
    print("✅ Database initialized")


telegram.add_handler(CommandHandler("start", start))
telegram.add_handler(CommandHandler("help", help_command))
telegram.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat,
    )
)


@app.get("/")
async def root():
    return {"status": "FIMA AI is running"}


async def run_bot():
    await post_init()

    await telegram.initialize()
    await telegram.start()
    await telegram.updater.start_polling()


async def run_api():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )

    server = uvicorn.Server(config)

    await server.serve()


async def main():
    await asyncio.gather(
        run_bot(),
        run_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())
