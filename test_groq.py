from groq import Groq

# Ваш новый ключ
API_KEY = "gsk_..."  # ваш ключ (не публикуйте)

client = Groq(api_key=API_KEY)

try:
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "Привет! Напиши слово 'успех'."}],
        model="llama-3.1-8b-instant",
        temperature=0.5,
        max_tokens=20,
    )
    print("Ответ Groq:")
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Ошибка: {e}")