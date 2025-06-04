import os
import logging
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# فعال‌سازی لاگ‌ها
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# توکن از محیط
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

bot = telegram.Bot(token=BOT_TOKEN)

# اتصال به Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("FMCBot").sheet1

# مراحل گفتگو
(
    ASK_NAME,
    ASK_PHONE,
    ASK_STUDENT_ID,
    CHOOSE_INSTRUMENT,
    CONFIRM,
) = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای ثبت‌نام لطفاً نام و نام خانوادگی خود را وارد کنید.")
    return ASK_NAME

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("شماره تلفن همراه خود را وارد کنید:")
    return ASK_PHONE

async def ask_student_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text.strip()
    await update.message.reply_text("شماره دانشجویی خود را وارد کنید:")
    return ASK_STUDENT_ID

async def choose_instrument(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["student_id"] = update.message.text.strip()
    keyboard = [
        [InlineKeyboardButton("پیانو", callback_data="پیانو")],
        [InlineKeyboardButton("گیتار", callback_data="گیتار")],
        [InlineKeyboardButton("ویولن", callback_data="ویولن")],
        [InlineKeyboardButton("تار", callback_data="تار")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً ساز موردنظر خود را انتخاب کنید:", reply_markup=reply_markup)
    return CHOOSE_INSTRUMENT

async def save_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    instrument = query.data
    user_data = context.user_data
    user_data["instrument"] = instrument

    # ذخیره در Google Sheet
    sheet.append_row([
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_data["name"],
        user_data["phone"],
        user_data["student_id"],
        query.from_user.username or "",
        instrument
    ])

    await query.edit_message_text("✅ ثبت‌نام شما با موفقیت انجام شد. ممنون!")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات ثبت‌نام لغو شد.")
    return ConversationHandler.END

# ساخت اپلیکیشن
application = Application.builder().token(BOT_TOKEN).build()

# تعریف گفتگو
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_student_id)],
        ASK_STUDENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_instrument)],
        CHOOSE_INSTRUMENT: [CallbackQueryHandler(save_data)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(conv_handler)

# راه‌اندازی Webhook
if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL,
    )
