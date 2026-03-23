import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
print("BOT_TOKEN =", BOT_TOKEN)

PROXY_URL = "socks5://127.0.0.1:1080"  # ваш прокси

class OrderStates(StatesGroup):
    waiting_for_vin = State()
    waiting_for_model = State()
    waiting_for_year = State()
    waiting_for_description = State()
    waiting_for_photo = State()

async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать! Введите VIN техники:")
    await state.set_state(OrderStates.waiting_for_vin)

async def process_vin(message: types.Message, state: FSMContext):
    await state.update_data(vin=message.text)
    await message.answer("Введите модель техники:")
    await state.set_state(OrderStates.waiting_for_model)

async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введите год выпуска:")
    await state.set_state(OrderStates.waiting_for_year)

async def process_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("Опишите проблему:")
    await state.set_state(OrderStates.waiting_for_description)

async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Можете отправить фото или /skip")
    await state.set_state(OrderStates.waiting_for_photo)

async def skip_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print("Заявка:", data)
    await message.answer("Заявка сохранена!")
    await state.clear()

async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print("Заявка с фото:", data)
    await message.answer("Заявка сохранена!")
    await state.clear()

async def incorrect_input(message: types.Message):
    await message.answer("Отправьте фото или /skip")

async def main():
    connector = ProxyConnector.from_url(PROXY_URL)
    session = AiohttpSession(connector=connector)
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.message.register(start_command, Command("start"))
    dp.message.register(process_vin, OrderStates.waiting_for_vin)
    dp.message.register(process_model, OrderStates.waiting_for_model)
    dp.message.register(process_year, OrderStates.waiting_for_year)
    dp.message.register(process_description, OrderStates.waiting_for_description)
    dp.message.register(skip_photo, Command("skip"))
    dp.message.register(process_photo, OrderStates.waiting_for_photo, lambda msg: msg.photo)
    dp.message.register(incorrect_input, OrderStates.waiting_for_photo)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())