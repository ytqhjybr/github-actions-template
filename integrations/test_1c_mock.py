# integrations/test_1c_mock.py
import sys
import os

# Добавляем корневую папку в путь, чтобы можно было импортировать модули
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.one_c_mock import mock_1c  # файл называется 1c_mock.py, но в импорте нельзя использовать цифру в начале

def test_create_order():
    result = mock_1c.create_order({"product": "tractor", "quantity": 2})
    assert result["success"] is True
    assert "order_id" in result
    print("✅ test_create_order passed")

def test_get_order():
    # Сначала создаём заказ
    create_result = mock_1c.create_order({"product": "plow"})
    order_id = create_result["order_id"]
    # Получаем его
    order = mock_1c.get_order(order_id)
    assert order["id"] == order_id
    assert order["data"]["product"] == "plow"
    print("✅ test_get_order passed")

def test_get_nonexistent_order():
    order = mock_1c.get_order(999)
    assert "error" in order
    print("✅ test_get_nonexistent_order passed")

if __name__ == "__main__":
    test_create_order()
    test_get_order()
    test_get_nonexistent_order()
    print("\n🎉 Все тесты 1C mock пройдены!")