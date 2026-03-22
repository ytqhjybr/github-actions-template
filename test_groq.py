import os
from openai import OpenAI

# Укажите ключ явно (замените на ваш ключ gsk_...)
api_key = "gsk_..."  # вставьте сюда один из ваших ключей

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Привет"}],
        max_tokens=10
    )
    print("Ответ:", completion.choices[0].message.content)
except Exception as e:
    print("Ошибка:", e)