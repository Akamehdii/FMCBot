import os
import logging
from datetime import datetime

from fastapi import FastAPI, Request
import telegram
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============ تنظیمات ============
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8443))

# ============ Google Sheet ============
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('google-credentials.json', scope)
client = gspread.authorize(credentials)
sheet = client.open("FMCBot").sheet1

# ============ FastAPI و Telegram ============
app = FastAPI()
bot = telegram.Bot(token=TOKEN)

application = Application.builder().token(TOKEN).build()

# ============ لیست سازها ============
instruments = ["🎹 پیانو", "🎸 گیتار", "🎻 ویولن", "🥁 درام", "🎤 آواز"]

# ============ توابع ربات ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(text=inst)] for inst in instruments]
    await update.message.reply_text(
        "سلام! برای ثبت‌نام، لطفاً ساز مورد علاقه‌ات رو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in instruments:
        context.user_data["instrument"] = text
        await update.message.reply_text("لطفاً نام و نام خانوادگی‌ات را وارد کن:")
    elif "instrument" in context.user_data and "name" not in context.user_data:
        context.user_data["name"] = text
        await update.message.reply_text("شماره تلفن همراه را وارد کن:")
    elif "name" in context.user_data and "phone" not in context.user_data:
        context.user_data["phone"] = text
        await update.message.reply_text("شماره دانشجویی را وارد کن:")
    elif "phone" in context.user_data and "student_id" not in context.user_data:
        context.user_data["student_id"] = text

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        telegram_id = update.message.from_user.id
        username = update.message.from_user.username or ""

        row = [
            now,
            context.user_data["name"],
            context.user_data["phone"],
            context.user_data["student_id"],
            f"@{username}" if username else telegram_id,
            context.user_data["instrument"]
        ]
        sheet.append_row(row)
        await update.message.reply_text("ثبت‌نام با موفقیت انجام شد ✅")

# ============ ثبت هندلرها ============
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ============ FastAPI Routes ============
@app.post(f"/{TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/ping")
async def ping():
    return {"status": "FMCBot is alive"}

# ============ راه‌اندازی Webhook ============
@app.on_event("startup")
async def on_startup():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
