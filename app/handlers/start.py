from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Я Фима-ИИ.\n"
        "Напиши мне любое сообщение, и я отвечу с помощью Gemini AI."
    )
