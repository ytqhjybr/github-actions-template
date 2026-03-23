import streamlit as st
import requests
import os
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Заявка на запчасти", layout="centered")
st.title("📝 Оформление заявки на запчасти")
st.markdown("Заполните форму, и наш ассистент обработает ваш запрос.")

# Сессия для хранения данных последней заявки
if "last_order" not in st.session_state:
    st.session_state.last_order = None

with st.form("order_form"):
    vin = st.text_input("VIN техники", placeholder="XTA211200R1234567")
    model = st.text_input("Модель техники", placeholder="МТЗ-82")
    year = st.text_input("Год выпуска", placeholder="2020")
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
            "photo_path": photo_path
        }
        try:
            response = requests.post(f"{API_URL}/save-order", json=payload)
            if response.status_code == 200:
                st.success("Заявка успешно отправлена! Спасибо.")
                st.balloons()
                # Сохраняем данные заявки в сессию
                st.session_state.last_order = payload
            else:
                st.error(f"Ошибка при отправке: {response.status_code}")
        except Exception as e:
            st.error(f"Не удалось соединиться с сервером: {e}")

# Кнопка для генерации КП, если есть сохранённая заявка
if st.session_state.last_order:
    if st.button("Сформировать коммерческое предложение по этой заявке"):
        order = st.session_state.last_order
        # Формируем запрос к /generate-from-template
        params = {
            "template_name": "template.docx",
            "client_name": order["model"],  # используем модель как название клиента
            "region": "Московская область",
            "specialization": "запчасти",
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
                # Ссылка для скачивания (пока просто текст)
                st.info(f"Скачать файл можно по пути: {data['output_file']}")
            else:
                st.error(f"Ошибка генерации КП: {response.status_code}")
        except Exception as e:
            st.error(f"Ошибка соединения: {e}")