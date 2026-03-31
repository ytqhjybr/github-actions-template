import streamlit as st
import requests
import os
from datetime import datetime
import sys

API_URL = "http://localhost:8000"

# Добавляем путь для импорта mock_1c
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from integrations.one_c_mock import mock_1c

st.set_page_config(page_title="AI Ассистенты для дилера", layout="wide")

# --- Боковое меню (6 модулей) ---
st.sidebar.title("Модули")
page = st.sidebar.radio("Выберите модуль", [
    "Продажи техники",
    "Продажи запчастей",
    "Сервисный ассистент (RAG)",
    "Ассистент закупщика",
    "Дашборд",
    "1C Mock"
])

# ===================== МОДУЛЬ 1: ПРОДАЖИ ТЕХНИКИ =====================
if page == "Продажи техники":
    st.title("🚜 Ассистент продавца техники")
    st.markdown("Заполните данные о клиенте и загрузите спецификацию для формирования КП.")

    # Кнопки работы с 1С
    col1c1, col1c2 = st.columns(2)
    with col1c1:
        if st.button("📤 Выгрузить все заявки в 1С (техника)"):
            result = mock_1c.export_order({"module": "tech", "timestamp": datetime.now().isoformat()}, "tech")
            st.success(f"Выгружено в 1С. ID выгрузки: {result.get('export_id')}")
    with col1c2:
        if st.button("📥 Загрузить заказы из 1С (техника)"):
            orders = mock_1c.import_orders("tech")
            st.json(orders)

    # Ссылка на скачивание пустого шаблона спецификации
    if os.path.exists("data/uploads/spec_template.xlsx"):
        with open("data/uploads/spec_template.xlsx", "rb") as f:
            st.download_button(
                label="📥 Скачать пустой шаблон спецификации (Excel)",
                data=f,
                file_name="spec_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    if "last_order_tech" not in st.session_state:
        st.session_state.last_order_tech = None

    with st.form("order_form_tech"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Наименование заказчика", placeholder="ООО 'Агро'")
            client_inn = st.text_input("ИНН заказчика", placeholder="1234567890")
        with col2:
            region = st.selectbox("Регион", ["Московская область", "Ленинградская область", "Краснодарский край"])
            specialization = st.selectbox("Специализация", ["растениеводство", "животноводство", "смешанное"])
        description = st.text_area("Описание потребности в технике", height=100)
        spec_file = st.file_uploader("Заполненная спецификация техники (Excel)", type=["xlsx"])
        submitted = st.form_submit_button("Отправить заявку")

    if submitted:
        if not client_name or not client_inn or not description:
            st.error("Пожалуйста, заполните все обязательные поля.")
        else:
            spec_path = None
            if spec_file:
                os.makedirs("data/uploads", exist_ok=True)
                spec_path = f"data/uploads/spec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{spec_file.name}"
                with open(spec_path, "wb") as f:
                    f.write(spec_file.getbuffer())
            payload = {
                "type": "tech",
                "description": description,
                "region": region,
                "specialization": specialization,
                "client_name": client_name,
                "client_inn": client_inn,
                "spec_path": spec_path
            }
            try:
                response = requests.post(f"{API_URL}/save-order", json=payload)
                if response.status_code == 200:
                    st.success("Заявка успешно отправлена! Спасибо.")
                    st.balloons()
                    st.session_state.last_order_tech = payload
                    # Автоматически выгружаем в 1С
                    export_result = mock_1c.export_order(payload, "tech")
                    st.info(f"📤 Заявка автоматически выгружена в 1С (ID: {export_result.get('export_id')})")
                else:
                    st.error(f"Ошибка при отправке: {response.status_code}")
            except Exception as e:
                st.error(f"Не удалось соединиться с сервером: {e}")

    if st.session_state.last_order_tech:
        if st.button("Сформировать коммерческое предложение по этой заявке"):
            order = st.session_state.last_order_tech
            params = {
                "template_name": "template_tech.docx",
                "client_name": order.get("client_name", "Клиент"),
                "region": order["region"],
                "specialization": order["specialization"],
                "price_list_name": "price_test.xlsx",
                "additional_params": {
                    "description": order["description"],
                    "spec_path": order.get("spec_path"),
                    "client_inn": order.get("client_inn")
                }
            }
            try:
                response = requests.post(f"{API_URL}/generate-from-template", params=params)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"КП сгенерировано! Файл: {data['output_file']}")
                    download_url = f"{API_URL}/download/{data['output_file']}"
                    st.markdown(f"[Скачать файл]({download_url})")
                    # Экспортируем КП в 1С
                    export_result = mock_1c.export_proposal(data)
                    st.info(f"📤 КП выгружено в 1С (ID: {export_result.get('proposal_id')})")
                else:
                    st.error(f"Ошибка генерации КП: {response.status_code}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

# ===================== МОДУЛЬ 2: ПРОДАЖИ ЗАПЧАСТЕЙ =====================
elif page == "Продажи запчастей":
    st.title("🔧 Ассистент продавца запчастей")
    st.markdown("Заполните форму, и наш ассистент обработает ваш запрос.")

    # Кнопки работы с 1С
    col1c1, col1c2 = st.columns(2)
    with col1c1:
        if st.button("📤 Выгрузить все заявки в 1С (запчасти)"):
            result = mock_1c.export_order({"module": "spare", "timestamp": datetime.now().isoformat()}, "spare")
            st.success(f"Выгружено в 1С. ID выгрузки: {result.get('export_id')}")
    with col1c2:
        if st.button("📥 Загрузить заказы из 1С (запчасти)"):
            orders = mock_1c.import_orders("spare")
            st.json(orders)

    if "last_order_spare" not in st.session_state:
        st.session_state.last_order_spare = None

    with st.form("order_form_spare"):
        col1, col2 = st.columns(2)
        with col1:
            vin = st.text_input("VIN техники", placeholder="XTA211200R1234567")
            model = st.text_input("Модель техники", placeholder="МТЗ-82")
            year = st.text_input("Год выпуска", placeholder="2020")
        with col2:
            client_name = st.text_input("Наименование заказчика", placeholder="ООО 'Агро'")
            client_inn = st.text_input("ИНН заказчика", placeholder="1234567890")
            region = st.selectbox("Регион", ["Московская область", "Ленинградская область", "Краснодарский край"])
            specialization = st.selectbox("Специализация", ["растениеводство", "животноводство", "смешанное"])
        description = st.text_area("Описание проблемы или нужных запчастей", height=100)
        photo = st.file_uploader("Фото (необязательно)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Отправить заявку")

    if submitted:
        if not vin or not model or not year or not description:
            st.error("Пожалуйста, заполните все обязательные поля.")
        else:
            photo_path = None
            if photo:
                os.makedirs("data/orders/photos", exist_ok=True)
                photo_path = f"data/orders/photos/photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())
            payload = {
                "type": "spare",
                "vin": vin,
                "model": model,
                "year": year,
                "description": description,
                "photo_path": photo_path,
                "region": region,
                "specialization": specialization,
                "client_name": client_name,
                "client_inn": client_inn
            }
            try:
                response = requests.post(f"{API_URL}/save-order", json=payload)
                if response.status_code == 200:
                    st.success("Заявка успешно отправлена! Спасибо.")
                    st.balloons()
                    st.session_state.last_order_spare = payload
                    export_result = mock_1c.export_order(payload, "spare")
                    st.info(f"📤 Заявка автоматически выгружена в 1С (ID: {export_result.get('export_id')})")
                else:
                    st.error(f"Ошибка при отправке: {response.status_code}")
            except Exception as e:
                st.error(f"Не удалось соединиться с сервером: {e}")

    if st.session_state.last_order_spare:
        if st.button("Сформировать коммерческое предложение по этой заявке"):
            order = st.session_state.last_order_spare
            params = {
                "template_name": "template.docx",
                "client_name": order.get("client_name", order["model"]),
                "region": order["region"],
                "specialization": order["specialization"],
                "price_list_name": "price_test.xlsx",
                "additional_params": {
                    "vin": order["vin"],
                    "year": order["year"],
                    "description": order["description"],
                    "client_inn": order.get("client_inn")
                }
            }
            try:
                response = requests.post(f"{API_URL}/generate-from-template", params=params)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"КП сгенерировано! Файл: {data['output_file']}")
                    download_url = f"{API_URL}/download/{data['output_file']}"
                    st.markdown(f"[Скачать файл]({download_url})")
                    export_result = mock_1c.export_proposal(data)
                    st.info(f"📤 КП выгружено в 1С (ID: {export_result.get('proposal_id')})")
                else:
                    st.error(f"Ошибка генерации КП: {response.status_code}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

# ===================== МОДУЛЬ 3: СЕРВИСНЫЙ АССИСТЕНТ (RAG) =====================
elif page == "Сервисный ассистент (RAG)":
    st.title("🔧 Ассистент сервисного инженера")
    st.markdown("Загрузите руководства по ремонту и эксплуатации, затем задавайте вопросы.")

    # Кнопки работы с 1С
    col1c1, col1c2 = st.columns(2)
    with col1c1:
        if st.button("📥 Загрузить документы из 1С для RAG"):
            docs = mock_1c.import_rag_docs()
            st.success(f"Загружено документов: {len(docs)}")
            st.json(docs)
    with col1c2:
        if st.button("📤 Выгрузить историю RAG в 1С"):
            # Имитация выгрузки последнего запроса
            result = mock_1c.export_rag_query({"query": "последний запрос", "answer": "тест", "timestamp": datetime.now().isoformat()})
            st.success(f"Выгружено в 1С. ID: {result.get('record_id')}")

    st.subheader("📄 Загрузка руководства")
    uploaded_pdf = st.file_uploader("Выберите PDF-файл", type=["pdf"])

    if uploaded_pdf:
        files = {"file": (uploaded_pdf.name, uploaded_pdf.getvalue(), "application/pdf")}
        try:
            response = requests.post(f"{API_URL}/upload-pdf/", files=files)
            if response.status_code == 200:
                data = response.json()
                st.success(f"Файл загружен и проиндексирован. Количество фрагментов: {data['chunks']}")
            else:
                st.error(f"Ошибка загрузки: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Ошибка соединения: {e}")

    st.subheader("❓ Задайте вопрос по руководствам")
    query = st.text_input("Ваш вопрос:", placeholder="Как заменить масло в двигателе?")
    if st.button("Получить ответ"):
        if not query:
            st.warning("Введите вопрос.")
        else:
            try:
                response = requests.post(f"{API_URL}/ask-rag", params={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    st.markdown("**Ответ:**")
                    st.write(data["answer"])
                    with st.expander("Показать найденные фрагменты"):
                        for i, chunk in enumerate(data["found_chunks"], 1):
                            st.text(f"[Фрагмент {i}]")
                            st.write(chunk)
                    # Экспортируем в 1С
                    export_result = mock_1c.export_rag_query({"query": query, "answer": data["answer"], "fragments": data["found_chunks"]})
                    st.info(f"📤 Запрос и ответ выгружены в 1С (ID: {export_result.get('record_id')})")
                else:
                    st.error(f"Ошибка: {response.status_code}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

# ===================== МОДУЛЬ 4: АССИСТЕНТ ЗАКУПЩИКА =====================
elif page == "Ассистент закупщика":
    st.title("📊 Ассистент закупщика")
    st.markdown("Загрузите файлы с данными для анализа и получите рекомендации по закупке.")

    # Кнопки работы с 1С
    col1c1, col1c2 = st.columns(2)
    with col1c1:
        if st.button("📥 Загрузить остатки из 1С"):
            stock = mock_1c.import_stock()
            st.success(f"Загружено позиций: {len(stock)}")
            st.dataframe(stock)
    with col1c2:
        if st.button("📤 Выгрузить анализ закупок в 1С"):
            result = mock_1c.export_stock_analysis({"timestamp": datetime.now().isoformat(), "status": "analyzed"})
            st.success(f"Анализ выгружен в 1С. ID: {result.get('analysis_id')}")

    with st.form("purchase_form"):
        stock_file = st.file_uploader("Остатки на складе (Excel)", type=["xlsx"])
        orders_file = st.file_uploader("Заказы клиентов (Excel, необязательно)", type=["xlsx"])
        in_transit_file = st.file_uploader("Заказы в пути (Excel, необязательно)", type=["xlsx"])
        sales_file = st.file_uploader("Статистика продаж (Excel, необязательно)", type=["xlsx"])
        safety_formula = st.text_input("Формула минимального остатка", value="mean_sales * 2 + min_stock")
        submitted = st.form_submit_button("Анализировать")

    if submitted and stock_file:
        files = {"stock_file": stock_file}
        if orders_file:
            files["orders_file"] = orders_file
        if in_transit_file:
            files["in_transit_file"] = in_transit_file
        if sales_file:
            files["sales_file"] = sales_file
        params = {"safety_stock_formula": safety_formula}

        try:
            response = requests.post(f"{API_URL}/analyze-stock", params=params, files=files)
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    st.error(data["error"])
                else:
                    st.success("Анализ выполнен!")
                    st.subheader("Рекомендуемый список закупки")
                    if data.get("purchase_list"):
                        st.dataframe(data["purchase_list"])
                    else:
                        st.info("Ничего не требуется закупать.")
                    with st.expander("Показать полные данные"):
                        st.json(data["full_data"])
                    # Экспортируем анализ в 1С
                    export_result = mock_1c.export_stock_analysis(data)
                    st.info(f"📤 Анализ выгружен в 1С (ID: {export_result.get('analysis_id')})")
            else:
                st.error(f"Ошибка: {response.status_code}")
        except Exception as e:
            st.error(f"Ошибка соединения: {e}")
    elif submitted and not stock_file:
        st.error("Файл остатков обязателен.")

# ===================== МОДУЛЬ 5: ДАШБОРД =====================
elif page == "Дашборд":
    st.title("📈 Дашборд аналитики")
    st.markdown("Статистика по заявкам и коммерческим предложениям.")

    # Кнопки работы с 1С
    col1c1, col1c2 = st.columns(2)
    with col1c1:
        if st.button("📥 Загрузить аналитику из 1С"):
            analytics = mock_1c.import_analytics()
            st.success(f"Загружено записей: {len(analytics)}")
            st.json(analytics)
    with col1c2:
        if st.button("📤 Выгрузить текущую аналитику в 1С"):
            try:
                response = requests.get(f"{API_URL}/analytics")
                if response.status_code == 200:
                    data = response.json()
                    export_result = mock_1c.export_analytics(data)
                    st.success(f"Аналитика выгружена в 1С. ID: {export_result.get('record_id')}")
                else:
                    st.error("Не удалось получить данные для выгрузки")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

    try:
        response = requests.get(f"{API_URL}/analytics")
        if response.status_code == 200:
            data = response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Всего заявок", data["total_orders"])
            with col2:
                st.metric("Всего КП", data["total_proposals"])
            
            if data["orders_by_region"]:
                st.subheader("Заявки по регионам")
                st.bar_chart(data["orders_by_region"])
            
            if data["orders_by_specialization"]:
                st.subheader("Заявки по специализации")
                st.bar_chart(data["orders_by_specialization"])
            
            if data["proposals_by_client"]:
                st.subheader("КП по клиентам")
                st.bar_chart(data["proposals_by_client"])
        else:
            st.error("Не удалось получить данные")
    except Exception as e:
        st.error(f"Ошибка соединения: {e}")

# ===================== МОДУЛЬ 6: 1C MOCK (для отладки) =====================
elif page == "1C Mock":
    st.title("🔄 Интеграция с 1С")
    st.markdown("Имитация работы с 1С. Создание и получение заказов.")

    st.subheader("📦 Создать заказ")
    with st.form("create_order_form"):
        product = st.text_input("Товар", placeholder="Трактор МТЗ-82")
        quantity = st.number_input("Количество", min_value=1, value=1)
        submitted_create = st.form_submit_button("Создать заказ в 1С")

    if submitted_create and product:
        result = mock_1c.create_order({"product": product, "quantity": quantity})
        if result.get("success"):
            st.success(f"Заказ №{result['order_id']} создан!")
        else:
            st.error("Ошибка создания заказа")

    st.subheader("🔍 Получить заказ")
    order_id = st.number_input("Номер заказа", min_value=1, step=1)
    if st.button("Получить заказ"):
        order = mock_1c.get_order(order_id)
        if "error" in order:
            st.error(order["error"])
        else:
            st.json(order)

    st.subheader("📊 Состояние 1С Mock")
    if st.button("Показать все данные"):
        st.json({
            "orders": mock_1c.orders,
            "proposals": mock_1c.proposals,
            "stock": mock_1c.stock,
            "rag_docs": mock_1c.rag_docs,
            "analytics": mock_1c.analytics
        })