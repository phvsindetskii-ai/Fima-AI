from telegram import Update
from telegram.ext import ContextTypes

from app.ai.gemini import ask_gemini


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing",
        )

        answer = await ask_gemini(
            user_id=update.effective_user.id,
            text=update.message.text,
        )

        await update.message.reply_text(answer)

    except Exception as e:
        print(f"Chat error: {e}")

        await update.message.reply_text(
            "❌ Произошла ошибка. Попробуй еще раз."
        )
