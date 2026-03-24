import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
print("BOT_TOKEN =", BOT_TOKEN)

if not BOT_TOKEN:
    print("Ошибка: TELEGRAM_BOT_TOKEN не найден в .env")
    exit(1)

class OrderStates(StatesGroup):
    waiting_for_vin = State()
    waiting_for_model = State()
    waiting_for_year = State()
    waiting_for_description = State()
    waiting_for_photo = State()

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    print("Получена команда /start")
    await message.answer("Добро пожаловать! Я помогу оформить заявку на запчасти.\nВведите VIN техники:")
    await state.set_state(OrderStates.waiting_for_vin)

@dp.message(OrderStates.waiting_for_vin)
async def process_vin(message: types.Message, state: FSMContext):
    print("Обработка VIN:", message.text)
    await state.update_data(vin=message.text)
    await message.answer("Введите модель техники:")
    await state.set_state(OrderStates.waiting_for_model)

@dp.message(OrderStates.waiting_for_model)
async def process_model(message: types.Message, state: FSMContext):
    print("Обработка модели:", message.text)
    await state.update_data(model=message.text)
    await message.answer("Введите год выпуска:")
    await state.set_state(OrderStates.waiting_for_year)

@dp.message(OrderStates.waiting_for_year)
async def process_year(message: types.Message, state: FSMContext):
    print("Обработка года:", message.text)
    await state.update_data(year=message.text)
    await message.answer("Опишите проблему или нужные запчасти:")
    await state.set_state(OrderStates.waiting_for_description)

@dp.message(OrderStates.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    print("Обработка описания:", message.text)
    await state.update_data(description=message.text)
    await message.answer("Можете отправить фото (необязательно). Или нажмите /skip, чтобы пропустить.")
    await state.set_state(OrderStates.waiting_for_photo)

@dp.message(Command("skip"))
async def skip_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print("Заявка (без фото):", data)
    await save_order(message.from_user.id, data, photo_file_id=None)
    await message.answer("Заявка сохранена! Спасибо.")
    await state.clear()

@dp.message(OrderStates.waiting_for_photo, lambda msg: msg.photo)
async def process_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    data = await state.get_data()
    print("Заявка с фото:", data)
    await save_order(message.from_user.id, data, photo_file_id=photo.file_id)
    await message.answer("Заявка сохранена! Спасибо.")
    await state.clear()

@dp.message(OrderStates.waiting_for_photo)
async def incorrect_input(message: types.Message):
    await message.answer("Пожалуйста, отправьте фото или нажмите /skip")

async def save_order(user_id, data, photo_file_id):
    print(f"Заявка от {user_id}:")
    print(f"VIN: {data['vin']}")
    print(f"Модель: {data['model']}")
    print(f"Год: {data['year']}")
    print(f"Описание: {data['description']}")
    print(f"Фото: {photo_file_id}")
    print("-" * 40)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())