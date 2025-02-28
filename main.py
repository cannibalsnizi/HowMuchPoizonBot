import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from flask import Flask
import threading

# Твой токен
TOKEN = "8117565230:AAHeYBMHJ6ylO4hYdRpITf3f8OTp13GsNaU"

# Константыф
EXCHANGE_RATE = 12.20  # Курс юаня
SERVICE_FEE = 1700  # Твой процент
DELIVERY_COST = 2000  # Доставка
EXTRA_FEE = 1000  # Дополнительная комиссия
MANAGER_USERNAME = "Gooseparis"  # Контакт менеджера

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранение данных пользователей
user_data = {}

# Клавиатура главного меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Рассчитать стоимость", callback_data="calculate")],
    [InlineKeyboardButton(text="🛍 Как заказать", callback_data="instruction")],
    [InlineKeyboardButton(text="💬 Связаться с менеджером", url=f"https://t.me/{MANAGER_USERNAME}")]
])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я помогу рассчитать стоимость заказа с Poizon.", reply_markup=main_menu)

@dp.callback_query(lambda c: c.data == "calculate")
async def ask_item_price(callback: types.CallbackQuery):
    await callback.message.answer("💰 Введите цену товара в юанях (CNY):")
    await callback.answer()

@dp.message()
async def process_price(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}

    if message.text.isdigit():
        price_cny = int(message.text)
        user_data[user_id]["price_cny"] = price_cny

        total_price = (price_cny * EXCHANGE_RATE) + SERVICE_FEE + DELIVERY_COST + EXTRA_FEE

        response_text = (
            f"💰 Цена товара: {price_cny} CNY\n"
            f"📈 Курс: {EXCHANGE_RATE}\n"
            f"🔄 Пересчитанная цена: {price_cny * EXCHANGE_RATE:.2f} ₽\n"
            f"💵 Комиссия: {SERVICE_FEE} ₽\n"
            f"🚚 Доставка: {DELIVERY_COST} ₽\n"
            f"✅ Итоговая цена: {total_price:.2f} ₽\n\n"
            f"🔗 **Скопируйте это сообщение и отправьте менеджеру @Gooseparis для оформления заказа!**"
        )

        await message.answer(response_text, reply_markup=main_menu)
        del user_data[user_id]

@dp.callback_query(lambda c: c.data == "instruction")
async def instruction(callback: types.CallbackQuery):
    text_parts = [
        "📖 **Как заказать товар с Poizon**\n\n"
        "✅ **1. Установи Poizon**\n"
        "📲 Скачай приложение Poizon в App Store или Google Play.\n"
        "🆕 Зарегистрируйся через WeChat, QQ или номер телефона.",

        "✅ **2. Найди товар**\n"
        "🔎 Введи название бренда или модели в поиск.\n"
        "🛒 Выбери нужный размер.",

        "✅ **3. Посмотри цену**\n"
        "💰 Цена в юанях (CNY) указана на странице товара.\n"
        "⚠️ Нам нужна **только цена товара**, без доставки в Китае.",

        "✅ **4. Введи цену в боте**\n"
        "✍ Отправь цену вручную, бот сам рассчитает итоговую стоимость.",

        "✅ **5. Получи ссылку для заказа**\n"
        "🔗 Отправь текст с расчетом менеджеру **@Gooseparis**.\n"
        "💳 Он уточнит детали и оформит заказ.",

        f"📌 **Все цены считаются по курсу** {EXCHANGE_RATE} ₽ за 1 CNY.\n"
        "🚚 Доставка и комиссия уже включены в расчет!"
    ]

    for part in text_parts:
        await callback.message.answer(part, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(1)

    await callback.answer()

# Функция запуска веб-сервера для UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

async def main():
    threading.Thread(target=run_web, daemon=True).start()  # Запуск веб-сервера
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())