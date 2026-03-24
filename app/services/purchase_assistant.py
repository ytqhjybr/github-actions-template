import pandas as pd
import os
import numpy as np

def analyze_stock(
    stock_path: str,
    orders_path: str,
    in_transit_path: str,
    sales_path: str,
    safety_stock_formula: str = "mean_sales * 2 + min_stock"
):
    """
    Анализирует данные и формирует рекомендации по закупке.
    """
    # Загружаем данные
    stock = pd.read_excel(stock_path)
    orders = pd.read_excel(orders_path) if orders_path and os.path.exists(orders_path) else pd.DataFrame()
    in_transit = pd.read_excel(in_transit_path) if in_transit_path and os.path.exists(in_transit_path) else pd.DataFrame()
    sales = pd.read_excel(sales_path) if sales_path and os.path.exists(sales_path) else pd.DataFrame()

    # Если нет файлов, возвращаем заглушку
    if stock.empty:
        return {"error": "Файл остатков обязателен"}

    # Предполагаем, что во всех файлах есть колонка "Код товара" или "Наименование"
    # Для простоты будем работать с колонкой "Код"
    if "Код" not in stock.columns:
        # Если колонки "Код" нет, используем первую колонку как идентификатор
        stock = stock.rename(columns={stock.columns[0]: "Код"})
    if "Остаток" not in stock.columns:
        stock["Остаток"] = 0  # если нет колонки остатка, считаем 0

    # Продажи (если есть) – группируем по коду
    if not sales.empty:
        if "Код" in sales.columns and "Количество" in sales.columns:
            sales_sum = sales.groupby("Код")["Количество"].sum().reset_index()
            sales_sum = sales_sum.rename(columns={"Количество": "Продажи"})
            stock = stock.merge(sales_sum, on="Код", how="left").fillna(0)
        else:
            stock["Продажи"] = 0
    else:
        stock["Продажи"] = 0

    # Заказы в пути (если есть)
    if not in_transit.empty:
        if "Код" in in_transit.columns and "Количество" in in_transit.columns:
            transit_sum = in_transit.groupby("Код")["Количество"].sum().reset_index()
            transit_sum = transit_sum.rename(columns={"Количество": "В пути"})
            stock = stock.merge(transit_sum, on="Код", how="left").fillna(0)
        else:
            stock["В пути"] = 0
    else:
        stock["В пути"] = 0

    # Формула минимального остатка (по умолчанию 10)
    min_stock = 10
    if "min_stock" in safety_stock_formula.lower():
        # Парсинг, но для простоты возьмём 10
        min_stock = 10

    # Прогноз потребности: средние продажи × 2 + минимальный остаток – (остаток + в пути)
    stock["Прогноз_потребности"] = stock["Продажи"] * 2 + min_stock - (stock["Остаток"] + stock["В пути"])
    # Отрицательное значение = избыток, приводим к 0 для закупки
    stock["Рекомендация"] = stock["Прогноз_потребности"].apply(lambda x: max(0, int(x)))

    # Формируем список закупки
    purchase_list = stock[stock["Рекомендация"] > 0][["Код", "Рекомендация"]]
    return {
        "status": "analyzed",
        "purchase_list": purchase_list.to_dict(orient="records"),
        "full_data": stock.to_dict(orient="records")
    }