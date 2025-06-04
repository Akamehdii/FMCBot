from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

TOKEN = "8094127608:AAGFgmkAeAFCKkfPknkHlVxlgjni3tCXSHQ"

# مراحل مکالمه
SELECTING_CLASS, GETTING_NAME = range(2)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎹 کلاس پیانو", callback_data="پیانو")],
        [InlineKeyboardButton("🎸 کلاس گیتار", callback_data="گیتار")],
        [InlineKeyboardButton("📖 مشاهده قوانین", callback_data="قوانین")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! لطفاً کلاس موردنظر رو انتخاب کن:", reply_markup=reply_markup)
    return SELECTING_CLASS

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "قوانین":
        await query.edit_message_text("قوانین ثبت‌نام:\n1. حضور منظم\n2. پرداخت کامل شهریه\n3. رعایت ادب و نظم")
        return ConversationHandler.END

    context.user_data["class"] = choice
    await query.edit_message_text(f"کلاس انتخابی شما: {choice}\nلطفاً نام خود را وارد کنید:")
    return GETTING_NAME

async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    class_selected = context.user_data.get("class")
    await update.message.reply_text(f"ثبت‌نام شما با نام **{name}** در کلاس **{class_selected}** با موفقیت انجام شد ✅")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ثبت‌نام لغو شد.")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECTING_CLASS: [CallbackQueryHandler(button_handler)],
        GETTING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)

app.run_polling()
