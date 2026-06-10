import os

# توكن البوت من BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# معرف الأدمن بتاعك - هاته من @userinfobot في تليجرام
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# مفتاح Gemini API من Google AI Studio
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# رابط قاعدة البيانات - Koyeb هيعمله لوحده
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")
