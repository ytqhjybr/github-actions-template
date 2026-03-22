def get_llm_response(prompt: str, system_prompt: str = "Ты полезный ассистент.") -> str:
    """
    Заглушка для имитации ответа LLM.
    В реальном проекте здесь будет вызов OpenRouter или другого API.
    """
    return f"[ЗАГЛУШКА] Получен запрос: {prompt}\nСистемный промпт: {system_prompt}"