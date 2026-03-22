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

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class OrderStates(StatesGroup):
    waiting_for_vin = State()
    waiting_for_model = State()
    waiting_for_year = State()
    waiting_for_description = State()
    waiting_for_photo = State()

@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    print("Получена команда /start")
    await message.answer("Добро пожаловать! Введите VIN техники:")
    await state.set_state(OrderStates.waiting_for_vin)

@dp.message(OrderStates.waiting_for_vin)
async def process_vin(message: types.Message, state: FSMContext):
    await state.update_data(vin=message.text)
    await message.answer("Введите модель техники:")
    await state.set_state(OrderStates.waiting_for_model)

@dp.message(OrderStates.waiting_for_model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введите год выпуска:")
    await state.set_state(OrderStates.waiting_for_year)

@dp.message(OrderStates.waiting_for_year)
async def process_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("Опишите проблему:")
    await state.set_state(OrderStates.waiting_for_description)

@dp.message(OrderStates.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Можете отправить фото или /skip")
    await state.set_state(OrderStates.waiting_for_photo)

@dp.message(Command("skip"))
async def skip_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print("Заявка:", data)
    await message.answer("Заявка сохранена!")
    await state.clear()

@dp.message(OrderStates.waiting_for_photo, lambda msg: msg.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print("Заявка с фото:", data)
    await message.answer("Заявка сохранена!")
    await state.clear()

@dp.message(OrderStates.waiting_for_photo)
async def incorrect_input(message: types.Message):
    await message.answer("Отправьте фото или /skip")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())