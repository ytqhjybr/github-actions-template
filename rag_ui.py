import streamlit as st
import requests
import os

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Ассистент сервисного инженера", layout="centered")
st.title("🔧 Ассистент сервисного инженера")
st.markdown("Загрузите руководства по ремонту и эксплуатации, затем задавайте вопросы.")

# --- Загрузка PDF ---
st.subheader("📄 Загрузка руководства")
uploaded_pdf = st.file_uploader("Выберите PDF-файл", type=["pdf"])

if uploaded_pdf:
    # Отправляем файл напрямую, без сохранения на диск
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

# --- Запрос к RAG ---
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
