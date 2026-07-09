import json
import re

import google.generativeai as genai

from app.config import GEMINI_API_KEY
from app.database.database import database


genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def extract_json(text: str):
    """
    Безопасно достает JSON
    даже если Gemini завернул его
    в ```json ... ```
    """

    text = text.strip()

    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        return None


async def save_memory(self, user_id: int, key: str, value: str):
    async with await self.connect() as db:

        cursor = await db.execute(
            """
            SELECT id
            FROM memories
            WHERE user_id = ?
            AND key = ?
            """,
            (user_id, key)
        )

        exists = await cursor.fetchone()

        if exists:

            await db.execute(
                """
                UPDATE memories
                SET value = ?
                WHERE user_id = ?
                AND key = ?
                """,
                (value, user_id, key)
            )

        else:

            await db.execute(
                """
                INSERT INTO memories(user_id,key,value)
                VALUES(?,?,?)
                """,
                (user_id, key, value)
            )

        await db.commit()

    prompt = f"""
Ты анализируешь сообщение пользователя.

Если в сообщении есть информация,
которую стоит помнить долго,
верни JSON.

Например:

[
  {{
    "key":"name",
    "value":"Филип"
  }},
  {{
    "key":"city",
    "value":"Киев"
  }}
]

Можно использовать любые ключи.

Если запоминать нечего,
верни:

[]

Сообщение:

{text}
"""

    try:

        response = model.generate_content(prompt)

        memories = extract_json(response.text)

        if not memories:
            return

        for memory in memories:

            key = memory.get("key")
            value = memory.get("value")

            if key and value:

                await database.save_memory(
                    user_id,
                    key,
                    value
                )

    except Exception as e:

        print("Memory error:", e)

async def ask_gemini(user_id: int, text: str):

    history = await database.get_history(user_id)
    memories = await database.get_memories(user_id)

    prompt = """
Ты — Чендлерс.

Ты дружелюбный, умный и естественный собеседник.

Никогда не говори, что ты Gemini.

Если знаешь что-то о пользователе из памяти —
используй это естественно.

"""

    if memories:

        prompt += "\n### Memory ###\n"

        for key, value in memories:

            prompt += f"{key}: {value}\n"

    prompt += "\n### Conversation ###\n"

    for role, message in history:

        prompt += f"{role}: {message}\n"

    prompt += f"\nuser: {text}\nassistant:"

    try:

        response = model.generate_content(prompt)

        answer = response.text

    except Exception:

        answer = (
            "Извини, сейчас я не смог ответить. "
            "Попробуй еще раз через пару секунд."

        )

    await database.save_message(

        user_id,

        "user",

        text

    )

    await database.save_message(

        user_id,

        "assistant",

        answer

    )

    await save_memories(

        user_id,

        text

    )

    return answer
