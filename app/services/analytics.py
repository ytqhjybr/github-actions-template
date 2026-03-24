import os
import json
import pandas as pd
from datetime import datetime

def get_orders_data():
    """Собирает данные из всех сохранённых заявок."""
    orders_dir = "data/orders"
    if not os.path.exists(orders_dir):
        return pd.DataFrame()
    
    orders = []
    for filename in os.listdir(orders_dir):
        if filename.endswith(".json") and filename.startswith("order_"):
            filepath = os.path.join(orders_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Добавляем дату из имени файла
                try:
                    date_str = filename.replace("order_", "").replace(".json", "")
                    data["date"] = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                except:
                    data["date"] = datetime.now()
                orders.append(data)
    
    return pd.DataFrame(orders)

def get_proposals_data():
    """Собирает данные из всех сгенерированных КП (из БД или из файлов)."""
    # Пока возвращаем пустой датафрейм, позже можно подключить БД
    # Для демо используем список из proposals
    proposals_dir = "data/proposals"
    if not os.path.exists(proposals_dir):
        return pd.DataFrame()
    
    proposals = []
    for filename in os.listdir(proposals_dir):
        if filename.endswith(".docx") and filename.startswith("proposal_"):
            # Извлекаем имя клиента и дату из имени файла
            name = filename.replace("proposal_", "").replace(".docx", "")
            # Получаем время создания файла
            filepath = os.path.join(proposals_dir, filename)
            mtime = os.path.getmtime(filepath)
            proposals.append({
                "client_name": name,
                "file": filename,
                "date": datetime.fromtimestamp(mtime)
            })
    
    return pd.DataFrame(proposals)