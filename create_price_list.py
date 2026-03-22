import openpyxl

# Создаём новую книгу Excel
wb = openpyxl.Workbook()
ws = wb.active

# Добавляем заголовки
ws.append(["Наименование", "Цена, руб"])
# Добавляем строки с техникой
ws.append(["Трактор МТЗ-82", 2500000])
ws.append(["Плуг ПН-4-35", 150000])
ws.append(["Сеялка СЗ-3,6", 800000])

# Сохраняем файл в папку data/uploads (создадим её, если нет)
import os
os.makedirs("data/uploads", exist_ok=True)
wb.save("data/uploads/price_list.xlsx")

print("Файл price_list.xlsx создан в папке data/uploads")