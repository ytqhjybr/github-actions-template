# integrations/one_c_mock.py
# Имитация 1C для тестов. Возвращает фейковые ответы.

class OneCMock:
    def __init__(self):
        self.orders = []          # заказы (для модуля запчастей и техники)
        self.proposals = []       # КП (для модуля техники и запчастей)
        self.stock = []           # остатки (для модуля закупщика)
        self.rag_docs = []        # документы RAG (для сервисного модуля)
        self.analytics = []       # аналитика (для дашборда)

    # ===== ОБЩИЕ МЕТОДЫ =====
    def create_order(self, order_data):
        """Создать заказ в 1С (фейк)."""
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

    def export_order(self, order_data, order_type):
        """Экспорт заявки в 1С (разные типы: tech, spare)"""
        export_id = len(self.orders) + 1
        fake_export = {
            "export_id": export_id,
            "type": order_type,
            "data": order_data,
            "status": "exported"
        }
        self.orders.append(fake_export)
        return {"success": True, "export_id": export_id}

    def import_orders(self, order_type=None):
        """Импорт заказов из 1С (можно фильтровать по типу)"""
        if order_type:
            return [o for o in self.orders if o.get("type") == order_type]
        return self.orders

    # ===== ДЛЯ МОДУЛЯ ТЕХНИКИ И ЗАПЧАСТЕЙ (КП) =====
    def export_proposal(self, proposal_data):
        """Экспорт КП в 1С"""
        proposal_id = len(self.proposals) + 1
        fake_proposal = {
            "id": proposal_id,
            "data": proposal_data,
            "status": "exported"
        }
        self.proposals.append(fake_proposal)
        return {"success": True, "proposal_id": proposal_id}

    def import_proposals(self):
        """Импорт КП из 1С"""
        return self.proposals

    # ===== ДЛЯ МОДУЛЯ ЗАКУПЩИКА (остатки) =====
    def export_stock_analysis(self, stock_data):
        """Экспорт результатов анализа остатков в 1С"""
        analysis_id = len(self.stock) + 1
        fake_analysis = {
            "id": analysis_id,
            "data": stock_data,
            "status": "exported"
        }
        self.stock.append(fake_analysis)
        return {"success": True, "analysis_id": analysis_id}

    def import_stock(self):
        """Импорт остатков из 1С (для анализа)"""
        # Для теста вернём фейковые остатки
        return [
            {"code": "TR-001", "name": "Трактор МТЗ-82", "stock": 5},
            {"code": "PL-003", "name": "Плуг ПН-4-35", "stock": 2},
        ]

    # ===== ДЛЯ СЕРВИСНОГО МОДУЛЯ (RAG) =====
    def export_rag_query(self, query_data):
        """Экспорт вопроса и ответа RAG в 1С"""
        record_id = len(self.rag_docs) + 1
        fake_record = {
            "id": record_id,
            "query": query_data.get("query"),
            "answer": query_data.get("answer"),
            "fragments": query_data.get("fragments"),
            "status": "exported"
        }
        self.rag_docs.append(fake_record)
        return {"success": True, "record_id": record_id}

    def import_rag_docs(self):
        """Импорт документов для RAG из 1С"""
        # Для теста вернём фейковые документы
        return [
            {"name": "Руководство по ремонту МТЗ-82.pdf", "content": "..."},
            {"name": "Инструкция по эксплуатации.pdf", "content": "..."},
        ]

    # ===== ДЛЯ ДАШБОРДА (аналитика) =====
    def export_analytics(self, analytics_data):
        """Экспорт аналитики в 1С"""
        record_id = len(self.analytics) + 1
        fake_record = {
            "id": record_id,
            "data": analytics_data,
            "status": "exported"
        }
        self.analytics.append(fake_record)
        return {"success": True, "record_id": record_id}

    def import_analytics(self):
        """Импорт аналитики из 1С"""
        return self.analytics


# Глобальный экземпляр для тестов
mock_1c = OneCMock()