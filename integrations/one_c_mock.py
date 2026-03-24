# integrations/one_c_mock.py
# Имитация 1C для тестов. Возвращает фейковые ответы.

class OneCMock:
    def __init__(self):
        self.orders = []  # Фейковые заказы

    def create_order(self, order_data):
        """Создать заказ в 1C (фейк)."""
        order_id = len(self.orders) + 1
        fake_order = {"id": order_id, "data": order_data, "status": "created"}
        self.orders.append(fake_order)
        return {"success": True, "order_id": order_id}

    def get_order(self, order_id):
        """Получить заказ (фейк)."""
        for order in self.orders:
            if order["id"] == order_id:
                return order
        return {"error": "Order not found"}

# Глобальный экземпляр для тестов
mock_1c = OneCMock()