import openpyxl
from typing import List, Dict

def read_price_list(file_path: str) -> List[Dict[str, any]]:
    """
    Читает Excel-файл с прайс-листом.
    Ожидает, что первая строка — заголовки.
    Возвращает список словарей с данными по каждой строке.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active

    # Получаем заголовки (первая строка)
    headers = []
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        if cell.value:
            headers.append(str(cell.value).strip())
        else:
            headers.append(f"Column{col}")

    # Читаем данные
    data = []
    for row in range(2, ws.max_row + 1):
        row_data = {}
        for col_idx, header in enumerate(headers, start=1):
            cell_value = ws.cell(row=row, column=col_idx).value
            row_data[header] = cell_value
        data.append(row_data)

    return data