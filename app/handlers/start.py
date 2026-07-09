from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я FIMA AI.\n"
        "Напиши любой вопрос, и я отвечу с помощью Gemini."
    )
