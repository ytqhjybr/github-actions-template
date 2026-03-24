import streamlit as st
import requests
import os
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Ассистенты для дилера", layout="wide")

# --- Боковое меню ---
st.sidebar.title("Модули")
page = st.sidebar.radio("Выберите модуль", ["Заявки и КП", "Сервисный ассистент (RAG)", "Ассистент закупщика"])

# ===================== СТРАНИЦА 1: ЗАЯВКИ И КП =====================
if page == "Заявки и КП":
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