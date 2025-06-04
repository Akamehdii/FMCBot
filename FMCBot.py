from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

TOKEN = os.environ.get("8094127608:AAGFgmkAeAFCKkfPknkHlVxlgjni3tCXSHQ")
PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_URL = os.environ.get("https://fmcbot.onrender.com/8094127608:AAGFgmkAeAFCKkfPknkHlVxlgjni3tCXSHQ")

# گوگل شیت
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("FMCBot").sheet1

instruments = [["🎹 پیانو", "🎸 گیتار"], ["🎻 ویولن", "🥁 درامز"]]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {}
    await update.message.reply_text("سلام! لطفاً نام و نام خانوادگی‌تان را وارد کنید:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {}

    if "name" not in user_data[user_id]:
        user_data[user_id]["name"] = message
        await update.message.reply_text("شماره تلفن همراهتان را وارد کنید:")
    elif "phone" not in user_data[user_id]:
        user_data[user_id]["phone"] = message
        await update.message.reply_text("شماره دانشجویی‌تان را وارد کنید:")
    elif "student_id" not in user_data[user_id]:
        user_data[user_id]["student_id"] = message
        keyboard = ReplyKeyboardMarkup(instruments, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("لطفاً ساز مورد نظر را انتخاب کنید:", reply_markup=keyboard)
    elif "instrument" not in user_data[user_id]:
        user_data[user_id]["instrument"] = message
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tg_username = update.effective_user.username or "-"
        row = [
            now,
            user_data[user_id]["name"],
            user_data[user_id]["phone"],
            user_data[user_id]["student_id"],
            tg_username,
            user_data[user_id]["instrument"]
        ]
        sheet.append_row(row)
        await update.message.reply_text("ثبت‌نام شما با موفقیت انجام شد. ✅")
        del user_data[user_id]

# اجرا با Webhook
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.bot.set_webhook(url=WEBHOOK_URL)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
