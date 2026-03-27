import asyncio
import logging
import os
import threading
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler

# Загружаем переменные окружения
load_dotenv()

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- КЛАВИАТУРА (всегда видна) ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Прислать афишу")],
        [KeyboardButton(text="💰 Разместить рекламу")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# --- ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ ---
welcome_text = (
    "🌟 *Добро пожаловать в бот канала «Афиша Минска»!* 🌟\n\n"
    "Я помогу вам разместить информацию о вашем мероприятии.\n\n"
    "Выберите нужный вариант ниже:"
)

# --- ПРОСТОЙ HTTP-СЕРВЕР ДЛЯ РЕНДЕРА ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_http_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- ОБРАБОТЧИКИ ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_kb
    )

@dp.message_handler(lambda message: message.text == "📅 Прислать афишу")
async def handle_send_event(message: types.Message):
    text = (
        "📝 *Здравствуйте!*\n\n"
        "На *бесплатной основе* мы размещаем афиши мероприятий в *новостном формате*, "
        "без обращений *«У нас»*, *«Мы»*, *«К нам»* и т.д.\n\n"
        "Мы публикуем новость от третьего лица, например:\n"
        "> «20 июня в Минске пройдет мастер-класс \\ концерт \\ акция». "
        "Далее описание мероприятия (что, где и когда).\n\n"
        "В бесплатном размещении Вы можете вставить ссылку *только на покупку билетов*.\n"
        "Ссылки чтобы узнать подробности и т.д. в бесплатном размещении *запрещены*.\n\n"
        "❌ *Афиши без оформления под формат — НЕ ПУБЛИКУЮТСЯ.*\n\n"
        "Если хотите охватить большую аудиторию и прорекламировать свое мероприятие, "
        "мы можем предложить вам эффективное и комплексное решение. "
        "Для этого нажмите на кнопку *«Разместить рекламу»*."
    )
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=main_kb
    )

@dp.message_handler(lambda message: message.text == "💰 Разместить рекламу")
async def handle_advertising(message: types.Message):
    ad_text = (
        "📢 *Реклама в канале «Афиша Минска»*\n\n"
        "Вы можете воспользоваться нашими платными услугами для продвижения вашего мероприятия:\n"
        "• Посты в крупнейших Инстаграм-аккаунтах Минска\n"
        "• Сторисы в Инстаграм \n\n"
        "• Посты в телеграм-каналах\n"
        "• Коллаборации с популярными блогерами \n\n"
        "📩 *Для связи с менеджером:*\n"
        "Напишите нашему менеджеру @stridiv"
    )
    await message.answer(
        ad_text,
        parse_mode="Markdown",
        reply_markup=main_kb
    )

@dp.message_handler()
async def handle_other_messages(message: types.Message):
    await message.answer(
        "Пожалуйста, используйте кнопки ниже для взаимодействия с ботом.",
        reply_markup=main_kb
    )

# --- ЗАПУСК БОТА С ВЕБ-СЕРВЕРОМ ---
async def main():
    print("🤖 Бот запущен и готов к работе...")
    # Запускаем HTTP-сервер в отдельном потоке
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    print(f"✅ HTTP-сервер запущен на порту {os.getenv('PORT', 10000)}")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
