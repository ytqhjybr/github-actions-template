from typing import List, Dict, Optional
from app.services.price_list_reader import read_price_list

def generate_proposal_text(
    region: str,
    specialization: str,
    price_list_path: Optional[str] = None,
    spec_path: Optional[str] = None,
    additional_params: dict = None
) -> str:
    """
    Генерация текста КП с использованием данных прайс-листа (если он загружен).
    Если прайс-лист не передан, возвращает заглушку.
    """
    # Базовый текст
    text = f"Сформировано предложение для региона {region}, специализация {specialization}.\n"

    # Если есть спецификация, добавляем информацию о ней
    if spec_path:
        text += f"\nЗагружена спецификация: {spec_path}\n"

    # Если есть прайс-лист, добавляем позиции
    if price_list_path:
        try:
            items = read_price_list(price_list_path)
            if items:
                text += "\nПредлагаемая техника и запчасти:\n"
                for item in items[:10]:  # показываем не больше 10 позиций
                    name = item.get("name") or item.get("Наименование", "Название не указано")
                    price = item.get("price") or item.get("Цена, руб", "цена не указана")
                    text += f"- {name}: {price} руб.\n"
                if len(items) > 10:
                    text += f"... и еще {len(items) - 10} позиций.\n"
            else:
                text += "Прайс-лист пуст или не содержит данных.\n"
        except Exception as e:
            text += f"Ошибка чтения прайс-листа: {e}\n"
    else:
        text += "Прайс-лист не предоставлен, формирую тестовое предложение.\n"

    # Дополнительные параметры (VIN, год, описание, ИНН)
    if additional_params:
        text += f"\nДополнительные параметры:\n"
        for key, value in additional_params.items():
            if value:
                text += f"- {key}: {value}\n"

    text += "\nЭто текст-заглушка. Позже здесь будет сгенерированное LLM описание техники и экономическое обоснование."
    return text