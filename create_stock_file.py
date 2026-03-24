import pandas as pd

# Данные: код товара и остаток
data = {
    "Код": ["TR-001", "TR-002", "PL-003", "SE-004", "CO-005"],
    "Остаток": [2, 5, 0, 1, 3]
}

df = pd.DataFrame(data)
df.to_excel("stock_test.xlsx", index=False)
print("Файл stock_test.xlsx создан")