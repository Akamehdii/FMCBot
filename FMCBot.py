from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # بخش راه‌اندازی ربات
    await application.bot.set_webhook(url=WEBHOOK_URL)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    print("Bot started via webhook.")
    
    yield  # اینجا برنامه اجرا میشه
    
    # بخش خاموش شدن ربات
    await application.updater.stop()
    await application.stop()
    await application.shutdown()
    print("Bot shutdown complete.")

app = FastAPI(lifespan=lifespan)

import os


BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# شروع ربات
welcome_text = (
    "سلام! به ربات کانون موسیقی خوش آمدید 🎶\n"
    "از طریق دکمه‌های زیر می‌تونید به بخش‌های مختلف دسترسی داشته باشید."
)

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
    [InlineKeyboardButton("سرپرست سلفژ پیشرفته", callback_data="sup_ssolfege2")],
    [InlineKeyboardButton("سرپرست دوتار", callback_data="sup_dotar")],
    [InlineKeyboardButton("سرپرست تار و سه‌تار", callback_data="sup_setar")],
    [InlineKeyboardButton("سرپرست سنتور", callback_data="sup_santoor")],
    [InlineKeyboardButton("دبیر کانون", callback_data="sup_deputy")],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("started"):
        await update.message.reply_text("دوباره خوش اومدی! 🎶\nاز منوی زیر استفاده کن:",
            reply_markup=InlineKeyboardMarkup(menu_buttons))
    else:
        context.user_data["started"] = True
        await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(menu_buttons))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "register":
        await query.edit_message_text("لطفاً یک کارگاه انتخاب کنید:", reply_markup=InlineKeyboardMarkup(register_buttons))

    elif data == "reserve":
        await query.edit_message_text(
            text="برای رزرو تمرین ساز به گروه زیر مراجعه کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به گروه رزرو تمرین 🎹", url="https://t.me/+R-b_fZzBVJs5OGQ0")]
            ])
        )

    elif data == "news":
        await query.edit_message_text("هنوز برنامه‌ای برای نشست این هفته تعیین نشده است.")

    elif data == "journal":
        await query.edit_message_text(
            "آخرین شماره نشریه ارغنون را از لینک زیر بخوانید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("مشاهده نشریه 📰", url="https://t.me/Ferdowsi_Music_Club/2154")]
            ])
        )

    elif data == "support":
        await query.edit_message_text("پشتیبانی را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(support_buttons))

    elif data.startswith("class_"):
        context.user_data["selected_class"] = data[6:]
        rules_text = """⚠️ ضوابط و قوانین شرکت در کلاس:

هنرجویان عزیز لطفا در مطالعه دقیق و رعایت موارد زیر کوشا باشید

🔴کلاس‌ها در ساختمان مجتمع کانون‌های فرهنگی هنری دانشگاه برگزار می‌شود.
🔴در صورتی که هنرجو قصد غیبت در کارگاه‌های ساز را داشته باشد، موظف است حداقل ۲۴ ساعت قبل به سرپرست اطلاع دهد.
🔴جلسات جبرانی برای غیبت برگزار نمی‌شود.
🔴در صورت تشکیل گروه، هنرجویان موظف به پیگیری پیام‌ها هستند.
🔴درصورت انصراف پیش از شروع جلسه اول، ۸۰٪ شهریه بازگردانده می‌شود.
⚠️پس از برگزاری کارگاه بازگشت وجه ممکن نیست حتی اگر هنرجو شرکت نکرده باشد.
🔴تعیین زمان کلاس فقط پس از واریز شهریه صورت می‌گیرد.
🔶انجام مراحل بعدی ثبت‌نام به معنای پذیرش تمام این شرایط است.
"""
        await query.edit_message_text(
            text=rules_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ برگشت", callback_data="register")],
                [InlineKeyboardButton("قبول دارم ✅", callback_data="accept_rules")]
            ])
        )

    elif data == "accept_rules":
        tuition_text = """🔴 مبلغ شهریه:

(ساز و آواز - ۸ جلسه انفرادی - هفته‌ای یک‌بار - نیم‌ساعته)  
(سلفژ مقدماتی - ۸ جلسه گروهی - هفته‌ای یک‌بار - یک‌ساعته)

🎓 برای دانشجویان دانشگاه فردوسی:
۹۹۰ هزار تومان برای سازها و آواز  
۸۵۰ هزار تومان برای سلفژ

👨‍🏫 برای اساتید و کارکنان دانشگاه فردوسی:
۱۲۰۰ هزار تومان برای سازها و آواز  
۹۵۰ هزار تومان برای سلفژ"""
        await query.edit_message_text(
            text=tuition_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("قبول دارم ✅", callback_data="accept_tuition")]
            ])
        )

    elif data == "accept_tuition":
        context.user_data["register_step"] = "name"
        await query.edit_message_text("لطفاً نام و نام خانوادگی خود را (فقط با حروف فارسی) ارسال کنید:")

    elif data.startswith("sup_"):
        await query.edit_message_text(f"آیدی پشتیبان: @{data[4:]}_support")

async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("register_step")

    if step == "name":
        if not all('\u0600' <= c <= '\u06FF' or c.isspace() for c in text):
            await update.message.reply_text("❗️ لطفاً نام و نام خانوادگی را فقط با حروف فارسی وارد کنید.")
            return
        context.user_data["name"] = text
        context.user_data["register_step"] = "student_id"
        await update.message.reply_text("شماره دانشجویی خود را وارد کنید:")
        return

    if step == "student_id":
        if not text.isdigit():
            await update.message.reply_text("❗️ شماره دانشجویی باید فقط شامل ارقام باشد.")
            return
        context.user_data["student_id"] = text
        context.user_data["register_step"] = "phone"
        contact_btn = ReplyKeyboardMarkup(
            [[KeyboardButton("📱 ارسال شماره تماس", request_contact=True)]],
            one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text("شماره موبایل خود را ارسال کنید:", reply_markup=contact_btn)
        return

    if step == "phone":
        if update.message.contact:
            phone_number = update.message.contact.phone_number
        else:
            phone_number = text
        context.user_data["phone"] = phone_number
        context.user_data["register_step"] = "card"
        await update.message.reply_text("لطفاً عکسی از کارت دانشجویی خود ارسال کنید:", reply_markup=ReplyKeyboardRemove())
        return

    if step == "card":
        if update.message.photo:
            context.user_data["card_photo"] = update.message.photo[-1].file_id
            context.user_data["register_step"] = "receipt"
            await update.message.reply_text(
                "🔺 لطفا مبلغ شهریه را به شماره کارت زیر واریز کرده و عکس فیش را ارسال کنید:\n\n"
                "6219-8619-0605-4340\n"
                "آیدین خلقی"
            )
        else:
            await update.message.reply_text("❗️ لطفاً یک عکس ارسال کنید.")
        return

    if step == "receipt":
        if update.message.photo:
            context.user_data["receipt_photo"] = update.message.photo[-1].file_id
            context.user_data["register_step"] = "done"
            await update.message.reply_text("✅ اطلاعات شما ثبت شد. لطفاً منتظر تایید نهایی بمانید.")
        else:
            await update.message.reply_text("❗️ لطفاً عکس فیش واریزی را ارسال کنید.")

application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))
application.add_handler(MessageHandler(filters.TEXT | filters.CONTACT | filters.PHOTO, handle_user_input))

@app.get("/")
async def root():
    return {"status": "FMCBot is alive"}

@app.on_event("startup")
async def on_startup():
    await application.bot.set_webhook(url=WEBHOOK_URL)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

@app.on_event("shutdown")
async def on_shutdown():
    await application.updater.stop()
    await application.stop()
    await application.shutdown()
