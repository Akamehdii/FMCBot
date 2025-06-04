import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

application = ApplicationBuilder().token(BOT_TOKEN).build()

# -- پیام‌ها --
welcome_text = (
    "سلام! به ربات کانون موسیقی خوش آمدید 🎶\n"
    "از طریق دکمه‌های زیر می‌تونید به بخش‌های مختلف دسترسی داشته باشید."
)

rules_text = (
    "⚠️ضوابط و قوانین شرکت در کلاس:\n\n"
    "هنرجویان عزیز لطفا در مطالعه دقیق و رعایت موارد زیر کوشا باشید\n\n"
    "🔴کلاس‌ها در ساختمان مجتمع کانون های فرهنگی هنری دانشگاه برگزار میشود.\n"
    "🔴در صورتی که هنرجو قصد غیبت در کارگاه‌های ساز را داشته باشد، موظف است از حداقل 24 ساعت قبل از آن جلسه، به سرپرست کارگاه اطلاع دهد.\n"
    "🔴 توجه داشته باشید برای غیبت هنرجو در کارگاه‌ها جلسات جبرانی برگزار نخواهد شد.\n"
    "🔴درصورتی که برای اطلاع رسانی گروه تشکیل داده شد هنرجویان موظف هستند گروه را چک کنند.\n"
    "🔴 درصورت انصراف از شرکت در هر کارگاهی، هنرجو موظف است تا پیش از آغاز جلسه اول آن کارگاه به مسئول مربوطه اعلام انصراف کند.\n"
    "در این صورت مقدار ۲۰٪ از شهریه پرداختی کسر شده، باقی آن (۸۰٪) برگردانده خواهد شد.\n"
    "⚠️پس از برگزاری کارگاه بازگشت وجه میسر نخواهد بود. (حتی اگر هنرجو در جلسات شرکت نکرده باشد)\n"
    "🔴تصویب زمان کلاس تنها پس از واریز وجه انجام میشود\n\n"
    "🔶انجام مراحل بعدی ثبت‌نام به معنای پذیرفتن تمام شرایط ذکر شده است."
)

fee_text = (
    "🔴 مبلغ شهریه\n\n"
    "(ساز و آواز: ۸ جلسه انفرادی - یک روز در هفته - نیم ساعت)\n"
    "(سلفژ مقدماتی: ۸ جلسه گروهی - یک روز در هفته - یک ساعت)\n\n"
    "📌 برای دانشجویان دانشگاه فردوسی:\n"
    "۹۹۰ هزار تومان برای سازها و آواز\n"
    "۸۵۰ هزار تومان برای سلفژ\n\n"
    "📌 برای اساتید و کارمندان دانشگاه:\n"
    "۱۲۰۰ هزار تومان برای سازها و آواز\n"
    "۹۵۰ هزار تومان برای سلفژ"
)

payment_text = (
    "🔺 لطفا مبلغ شهریه خود را تا پیش از آغاز کارگاه به شماره حساب زیر واریز نمایید و تصویر فیش واریزی را ارسال کنید.\n\n"
    "💳 6219 8619 0605 4340\n"
    "آیدین خلقی"
)

# -- دکمه‌ها --
menu_buttons = [
    [InlineKeyboardButton("🎼 ثبت نام کارگاه های موسیقی", callback_data="register")],
    [InlineKeyboardButton("🎹 رزرو تمرین ساز", callback_data="reserve")],
    [InlineKeyboardButton("📰 اخبار نشست ها", callback_data="news")],
    [InlineKeyboardButton("📖 نشریه ارغنون", callback_data="journal")],
    [InlineKeyboardButton("🛠️ پشتیبانی", callback_data="support")],
]

register_buttons = [
    [InlineKeyboardButton("پیانو", callback_data="class_piano")],
    [InlineKeyboardButton("گیتار", callback_data="class_guitar")],
    [InlineKeyboardButton("کمانچه و ویولن", callback_data="class_violin")],
    [InlineKeyboardButton("دف و تنبک", callback_data="class_tonbak")],
    [InlineKeyboardButton("سلفژ مقدماتی", callback_data="class_solfege1")],
    [InlineKeyboardButton("سلفژ پیشرفته", callback_data="class_solfege2")],
    [InlineKeyboardButton("آواز", callback_data="class_vocal")],
    [InlineKeyboardButton("دوتار", callback_data="class_dotar")],
    [InlineKeyboardButton("تار و سه‌تار", callback_data="class_setar")],
    [InlineKeyboardButton("سنتور", callback_data="class_santoor")],
]

support_buttons = [
    [InlineKeyboardButton("سرپرست پیانو", callback_data="sup_piano")],
    [InlineKeyboardButton("سرپرست گیتار", callback_data="sup_guitar")],
    [InlineKeyboardButton("سرپرست آواز", callback_data="sup_vocal")],
    [InlineKeyboardButton("سرپرست کمانچه و ویولن", callback_data="sup_violin")],
    [InlineKeyboardButton("سرپرست دف و تنبک", callback_data="sup_tonbak")],
    [InlineKeyboardButton("سرپرست سلفژ مقدماتی", callback_data="sup_solfege1")],
    [InlineKeyboardButton("سرپرست سلفژ پیشرفته", callback_data="sup_solfege2")],
    [InlineKeyboardButton("سرپرست دوتار", callback_data="sup_dotar")],
    [InlineKeyboardButton("سرپرست تار و سه‌تار", callback_data="sup_setar")],
    [InlineKeyboardButton("سرپرست سنتور", callback_data="sup_santoor")],
    [InlineKeyboardButton("دبیر کانون", callback_data="sup_deputy")],
]

# -- متدهای هندل --
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(menu_buttons))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "register":
        await query.edit_message_text("لطفاً یک کارگاه انتخاب کنید:", reply_markup=InlineKeyboardMarkup(register_buttons))

    elif data.startswith("class_"):
        context.user_data["selected_class"] = data
        await query.edit_message_text(rules_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ قبول دارم", callback_data="accept_rules")],
            [InlineKeyboardButton("↩️ بازگشت", callback_data="register")]
        ]))

    elif data == "accept_rules":
        await query.edit_message_text(fee_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ متوجه شدم", callback_data="accept_fee")],
        ]))

    elif data == "accept_fee":
        await query.edit_message_text("لطفا نام و نام خانوادگی خود را به فارسی وارد کنید:")

        context.user_data["step"] = "name"

    elif data == "reserve":
        await query.edit_message_text(
            "برای رزرو تمرین ساز به گروه زیر مراجعه کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به گروه رزرو تمرین 🎹", url="https://t.me/+R-b_fZzBVJs5OGQ0")]
            ])
        )

    elif data == "news":
        await query.edit_message_text("هنوز برنامه‌ای برای نشست این هفته تعیین نشده است.")

    elif data == "journal":
        await query.edit_message_text("آخرین شماره نشریه ارغنون را از لینک زیر بخوانید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("مشاهده نشریه 📰", url="https://t.me/Ferdowsi_Music_Club/2154")]
            ]))

    elif data == "support":
        await query.edit_message_text("پشتیبانی را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(support_buttons))

    elif data.startswith("sup_"):
        await query.edit_message_text(f"آیدی پشتیبان: @{data[4:]}_support")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    step = user_data.get("step")

    if step == "name":
        if all('\u0600' <= c <= '\u06FF' or c.isspace() for c in update.message.text):
            user_data["name"] = update.message.text
            user_data["step"] = "student_id"
            await update.message.reply_text("شماره دانشجویی خود را وارد کنید:")
        else:
            await update.message.reply_text("لطفا نام را به فارسی وارد کنید.")

    elif step == "student_id":
        if update.message.text.isdigit():
            user_data["student_id"] = update.message.text
            user_data["step"] = "phone"
            contact_btn = ReplyKeyboardMarkup([
                [KeyboardButton("ارسال شماره تماس 📱", request_contact=True)]
            ], resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text("شماره تلفن همراه خود را وارد کنید یا ارسال را بزنید:", reply_markup=contact_btn)
        else:
            await update.message.reply_text("شماره دانشجویی باید فقط شامل عدد باشد.")

    elif step == "phone":
        user_data["phone"] = update.message.text
        user_data["step"] = "student_card"
        await update.message.reply_text("لطفاً عکس کارت دانشجویی خود را ارسال کنید.")

    elif step == "student_card":
        user_data["step"] = "payment"
        await update.message.reply_text(payment_text)

    elif step == "payment":
        user_data["step"] = "done"
        await update.message.reply_text("✅ لطفاً منتظر بمانید تا اطلاعات شما بررسی و تأیید شود.")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") == "phone":
        context.user_data["phone"] = update.message.contact.phone_number
        context.user_data["step"] = "student_card"
        await update.message.reply_text("لطفاً عکس کارت دانشجویی خود را ارسال کنید.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") == "student_card":
        context.user_data["step"] = "payment"
        await update.message.reply_text(payment_text)

# -- ثبت هندلرها --
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# -- FastAPI با Lifespan --
@asynccontextmanager
async def lifespan(app: FastAPI):
    await application.bot.set_webhook(url=WEBHOOK_URL)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    yield
    await application.updater.stop()
    await application.stop()
    await application.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "FMCBot is running."}
