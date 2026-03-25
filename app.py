import streamlit as st
import requests
import os
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Ассистенты для дилера", layout="wide")

# --- Боковое меню ---
st.sidebar.title("Модули")
page = st.sidebar.radio("Выберите модуль", [
    "Продажа техники",
    "Заявки и КП",
    "Сервисный ассистент (RAG)",
    "Ассистент закупщика",
    "Дашборд"
])

# ===================== СТРАНИЦА 0: ПРОДАЖА ТЕХНИКИ =====================
if page == "Продажа техники":
    st.title("🚜 Ассистент продавца техники")
    st.markdown("Сформируйте коммерческое предложение на технику по спецификации клиента.")

    if "last_proposal_data" not in st.session_state:
        st.session_state.last_proposal_data = None
    if "last_proposal_file" not in st.session_state:
        st.session_state.last_proposal_file = None

    with st.form("tech_form"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Название клиента", placeholder="ООО Агро")
            client_inn = st.text_input("ИНН клиента", placeholder="1234567890")
            region = st.selectbox("Регион", ["Московская область", "Ленинградская область", "Краснодарский край", "Ростовская область", "Ставропольский край"])
        with col2:
            specialization = st.selectbox("Специализация", ["растениеводство", "животноводство", "смешанное"])
            spec_file = st.file_uploader("Спецификация техники (Excel/PDF)", type=["xlsx", "pdf"])
        description = st.text_area("Дополнительные требования", height=80, placeholder="Укажите особые условия, сроки поставки и т.д.")
        submitted = st.form_submit_button("Сформировать КП")

    if submitted:
        if not client_name or not client_inn or not region or not specialization:
            st.error("Пожалуйста, заполните все обязательные поля.")
        else:
            spec_path = None
            if spec_file:
                os.makedirs("data/uploads", exist_ok=True)
                spec_path = f"data/uploads/spec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{spec_file.name.split('.')[-1]}"
                with open(spec_path, "wb") as f:
                    f.write(spec_file.getbuffer())
            params = {
                "template_name": "template.docx",
                "client_name": client_name,
                "region": region,
                "specialization": specialization,
                "price_list_name": "price_test.xlsx",
                "additional_params": {
                    "inn": client_inn,
                    "description": description,
                    "spec_file": spec_path
                }
            }
            try:
                response = requests.post(f"{API_URL}/generate-from-template", params=params)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"КП сгенерировано! Файл: {data['output_file']}")
                    download_url = f"{API_URL}/download/{data['output_file']}"
                    st.markdown(f"[Скачать файл]({download_url})")
                    st.session_state.last_proposal_data = {
                        "client_name": client_name,
                        "client_inn": client_inn,
                        "region": region,
                        "specialization": specialization,
                        "description": description
                    }
                    st.session_state.last_proposal_file = data["output_file"]
                else:
                    st.error(f"Ошибка генерации КП: {response.status_code}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

    # Кнопка отправки в 1С (появляется после успешной генерации КП)
    if st.session_state.last_proposal_data:
        st.divider()
        st.subheader("📤 Интеграция с 1С")
        if st.button("Отправить заказ в 1С (mock)"):
            order_data = {
                "client_name": st.session_state.last_proposal_data["client_name"],
                "client_inn": st.session_state.last_proposal_data["client_inn"],
                "region": st.session_state.last_proposal_data["region"],
                "specialization": st.session_state.last_proposal_data["specialization"],
                "description": st.session_state.last_proposal_data["description"],
                "proposal_file": st.session_state.last_proposal_file
            }
            try:
                # Отправляем запрос к эндпоинту 1С (добавим в main.py позже)
                response = requests.post(f"{API_URL}/send-to-1c", json=order_data)
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Заказ отправлен в 1С. Номер заказа: {result.get('order_id', 'N/A')}")
                    st.info(f"Ответ 1С: {result.get('message', '')}")
                else:
                    st.error(f"Ошибка отправки в 1С: {response.status_code}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

# ===================== СТРАНИЦА 1: ЗАЯВКИ И КП =====================
elif page == "Заявки и КП":
    st.title("📝 Оформление заявки на запчасти")
    st.markdown("Заполните форму, и наш ассистент обработает ваш запрос.")

    if "last_order" not in st.session_state:
        st.session_state.last_order = None

    with st.form("order_form"):
        col1, col2 = st.columns(2)
        with col1:
            vin = st.text_input("VIN техники", placeholder="XTA211200R1234567")
            model = st.text_input("Модель техники", placeholder="МТЗ-82")
            year = st.text_input("Год выпуска", placeholder="2020")
        with col2:
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
                "vin": vin,
                "model": model,
                "year": year,
                "description": description,
                "photo_path": photo_path,
                "region": region,
                "specialization": specialization
            }
            try:
                response = requests.post(f"{API_URL}/save-order", json=payload)
                if response.status_code == 200:
                    st.success("Заявка успешно отправлена! Спасибо.")
                    st.balloons()
                    st.session_state.last_order = payload
                else:
                    st.error(f"Ошибка при отправке: {response.status_code}")
            except Exception as e:
                st.error(f"Не удалось соединиться с сервером: {e}")

    if st.session_state.last_order:
        if st.button("Сформировать коммерческое предложение по этой заявке"):
            order = st.session_state.last_order
            params = {
                "template_name": "template.docx",
                "client_name": order["model"],
                "region": order["region"],
                "specialization": order["specialization"],
                "price_list_name": "price_test.xlsx",
                "additional_params": {
                    "vin": order["vin"],
                    "year": order["year"],
                    "description": order["description"]
                }
            }
            try:
                response = requests.post(f"{API_URL}/generate-from-template", params=params)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"КП сгенерировано! Файл: {data['output_file']}")
                    download_url = f"{API_URL}/download/{data['output_file']}"
                    st.markdown(f"[Скачать файл]({download_url})")
                else:
                    st.error(f"Ошибка генерации КП: {response.status_code}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

# ===================== СТРАНИЦА 2: RAG =====================
elif page == "Сервисный ассистент (RAG)":
    st.title("🔧 Ассистент сервисного инженера")
    st.markdown("Загрузите руководства по ремонту и эксплуатации, затем задавайте вопросы.")

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
                else:
                    st.error(f"Ошибка: {response.status_code}")
            except Exception as e:
                st.error(f"Ошибка соединения: {e}")

# ===================== СТРАНИЦА 3: АССИСТЕНТ ЗАКУПЩИКА =====================
elif page == "Ассистент закупщика":
    st.title("📊 Ассистент закупщика")
    st.markdown("Загрузите файлы с данными для анализа и получите рекомендации по закупке.")

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
            else:
                st.error(f"Ошибка: {response.status_code}")
        except Exception as e:
            st.error(f"Ошибка соединения: {e}")
    elif submitted and not stock_file:
        st.error("Файл остатков обязателен.")

# ===================== СТРАНИЦА 4: ДАШБОРД =====================
elif page == "Дашборд":
    st.title("📈 Дашборд аналитики")
    st.markdown("Статистика по заявкам и коммерческим предложениям.")
    
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