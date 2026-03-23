import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Читаем ключ OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY:
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    USE_REAL_LLM = True
    print("OpenRouter инициализирован")
else:
    USE_REAL_LLM = False
    print("ВНИМАНИЕ: OPENROUTER_API_KEY не найден, используется заглушка.")

def get_llm_response(prompt: str, system_prompt: str = "Ты полезный ассистент.") -> str:
    """
    Отправляет запрос в OpenRouter (если есть ключ) или возвращает заглушку.
    """
    if not USE_REAL_LLM:
        return f"[ЗАГЛУШКА] Запрос получен. Для получения реального ответа добавьте OPENROUTER_API_KEY в файл .env"

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Ошибка при обращении к OpenRouter: {e}"