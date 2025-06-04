from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, MessageHandler, filters
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# توکن بات تلگرام
TOKEN = "8094127608:AAGFgmkAeAFCKkfPknkHlVxlgjni3tCXSHQ"

# مراحل گفتگو
SELECTING_CLASS, GETTING_NAME, GETTING_PHONE, GETTING_STUDENT_ID = range(4)

# ارسال منوی ابتدایی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎹 کلاس پیانو", callback_data="پیانو")],
        [InlineKeyboardButton("🎸 کلاس گیتار", callback_data="گیتار")],
        [InlineKeyboardButton("📖 مشاهده قوانین", callback_data="قوانین")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! لطفاً کلاس موردنظر را انتخاب کنید:", reply_markup=reply_markup)
    return SELECTING_CLASS

# پاسخ به انتخاب کلاس یا قوانین
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "قوانین":
        await query.edit_message_text("📌 قوانین ثبت‌نام:\n1. حضور منظم\n2. پرداخت کامل شهریه\n3. رعایت ادب و نظم")
        return ConversationHandler.END

    context.user_data["class"] = choice
    await query.edit_message_text(f"کلاس انتخابی شما: {choice}\nلطفاً نام و نام خانوادگی خود را وارد کنید:")
    return GETTING_NAME

# گرفتن نام
async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("شماره تلفن همراه خود را وارد کنید:")
    return GETTING_PHONE

# گرفتن شماره تماس
async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("شماره دانشجویی خود را وارد کنید:")
    return GETTING_STUDENT_ID

# گرفتن شماره دانشجویی و ثبت نهایی
async def student_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["student_id"] = update.message.text
    user_id = update.message.from_user.username or update.message.from_user.id

    # ثبت در Google Sheet
    write_to_sheet(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        context.user_data["name"],
        context.user_data["phone"],
        context.user_data["student_id"],
        user_id,
        context.user_data["class"]
    )

    await update.message.reply_text("✅ ثبت‌نام شما با موفقیت انجام شد. ممنون از شما!")
    return ConversationHandler.END

# تابع لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ثبت‌نام لغو شد.")
    return ConversationHandler.END

# ثبت اطلاعات در Google Sheet
def write_to_sheet(time, name, phone, student_id, telegram_id, selected_class):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("FMCBot").sheet1
    sheet.append_row([time, name, phone, student_id, str(telegram_id), selected_class])

# راه‌اندازی بات
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECTING_CLASS: [CallbackQueryHandler(button_handler)],
        GETTING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
        GETTING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler)],
        GETTING_STUDENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_id_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)

app.run_polling()
