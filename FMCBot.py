import os
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters
)

# --- متغیرهای محیطی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# شناسه عددی گروه ادمین‌ها
GROUP_CHAT_ID = -4881825561

# !!! توجه: لینک گروه‌های کلاسی خود را اینجا وارد کنید !!!
CLASS_LINKS = {
    "class_piano": "https://t.me/joinchat/YOUR_PIANO_LINK",
    "class_guitar": "https://t.me/joinchat/YOUR_GUITAR_LINK",
    "class_violin": "https://t.me/joinchat/YOUR_VIOLIN_LINK",
    "class_tonbak": "https://t.me/joinchat/YOUR_TONBAK_LINK",
    "class_solfege1": "https://t.me/joinchat/YOUR_SOLFEGE1_LINK",
    "class_solfege2": "https://t.me/joinchat/YOUR_SOLFEGE2_LINK",
    "class_vocal": "https://t.me/joinchat/YOUR_VOCAL_LINK",
    "class_dotar": "https://t.me/joinchat/YOUR_DOTAR_LINK",
    "class_setar": "https://t.me/joinchat/YOUR_SETAR_LINK",
    "class_santoor": "https://t.me/joinchat/YOUR_SANTOOR_LINK",
}

# --- کیبورد دائمی و اصلی (بخش جدید) ---
main_reply_keyboard = ReplyKeyboardMarkup(
    [["شروع مجدد 🔄", "لغو عملیات ❌"]],
    resize_keyboard=True
)

application = ApplicationBuilder().token(BOT_TOKEN).build()

# -- پیام‌ها و دکمه‌ها --
welcome_text = (
    "سلام! به ربات کانون موسیقی خوش آمدید 🎶\n"
    "از طریق دکمه‌های زیر می‌تونید به بخش‌های مختلف دسترسی داشته باشید."
)
# ... (بقیه متغیرهای متنی شما بدون تغییر اینجا قرار می‌گیرند) ...
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
]

# -- متدهای هندل --
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # --- اصلاح شده: ارسال کیبورد اصلی ---
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_reply_keyboard  # <-- کیبورد دائمی اضافه شد
    )
    # ارسال منوی شیشه‌ای در یک پیام جداگانه
    await update.message.reply_text(
        "لطفا یک گزینه را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(menu_buttons)
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    # --- اصلاح شده: نمایش کیبورد اصلی پس از لغو ---
    await update.message.reply_text(
        "فرآیند ثبت‌نام لغو شد.",
        reply_markup=main_reply_keyboard # <-- کیبورد دائمی نمایش داده می‌شود
    )
    # حذف کیبورد موقتی مثل 'ارسال شماره'
    await update.message.reply_text("برای شروع مجدد، دکمه مربوطه را بزنید.", reply_markup=ReplyKeyboardRemove())
    await start(update, context)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data.startswith("approve_"):
        try:
            _, student_chat_id, class_name = data.split("_", 2)
            student_chat_id = int(student_chat_id)
            group_link = CLASS_LINKS.get(class_name)

            if group_link:
                approval_message = (
                    "🎉 ثبت‌نام شما در کارگاه موسیقی تایید شد!\n\n"
                    "لطفاً از طریق لینک زیر وارد گروه کلاس خود شوید:"
                )
                await context.bot.send_message(
                    chat_id=student_chat_id,
                    text=approval_message,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ورود به گروه کلاس", url=group_link)]])
                )
                admin_first_name = query.from_user.first_name
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ توسط {admin_first_name} تایید شد", callback_data="approved")]]))
            else:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚠️ لینک تعریف نشده", callback_data="link_error")]]))
        except Exception as e:
            print(f"Error in approval callback: {e}")
            await query.answer("خطایی در پردازش رخ داد.", show_alert=True)
        return

    if data == "register":
        await query.edit_message_text("لطفاً یک کارگاه انتخاب کنید:", reply_markup=InlineKeyboardMarkup(register_buttons))
    # ... (بقیه کدهای این تابع بدون تغییر باقی می‌مانند) ...
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (این تابع بدون تغییر باقی می‌ماند) ...
    user_data = context.user_data
    step = user_data.get("step")
    text = update.message.text

    if step == "name":
        if all('\u0600' <= c <= '\u06FF' or c.isspace() for c in text):
            user_data["name"] = text
            user_data["step"] = "student_id"
            await update.message.reply_text("شماره دانشجویی خود را وارد کنید:")
        else:
            await update.message.reply_text("لطفا نام را به فارسی و صحیح وارد کنید.")
    elif step == "student_id":
        if text.isdigit() and len(text) > 5:
            user_data["student_id"] = text
            user_data["step"] = "phone"
            contact_btn = ReplyKeyboardMarkup(
                [[KeyboardButton("ارسال شماره تماس 📱", request_contact=True)]],
                resize_keyboard=True, one_time_keyboard=True
            )
            await update.message.reply_text("شماره تلفن همراه خود را وارد کنید یا دکمه زیر را بزنید:", reply_markup=contact_btn)
        else:
            await update.message.reply_text("شماره دانشجویی باید فقط شامل عدد باشد. لطفا مجددا وارد کنید.")
    elif step == "phone":
        user_data["phone"] = text
        user_data["step"] = "student_card"
        await update.message.reply_text("لطفاً عکس کارت دانشجویی خود را ارسال کنید.", reply_markup=ReplyKeyboardRemove())


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") == "phone":
        context.user_data["phone"] = update.message.contact.phone_number
        context.user_data["step"] = "student_card"
        await update.message.reply_text("متشکرم. حالا لطفاً عکس کارت دانشجویی خود را ارسال کنید.", reply_markup=ReplyKeyboardRemove())

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (این تابع تقریباً بدون تغییر باقی می‌ماند) ...
    step = context.user_data.get("step")

    if step == "student_card":
        context.user_data["student_card_id"] = update.message.photo[-1].file_id
        context.user_data["step"] = "payment"
        await update.message.reply_text(payment_text)

    elif step == "payment":
        payment_receipt_id = update.message.photo[-1].file_id
        await update.message.reply_text("""✅ ثبت‌نام شما با موفقیت انجام شد. اطلاعات شما برای بررسی به شورای کانون ارسال گردید. متشکرم!""", reply_markup=main_reply_keyboard)

        user_info = context.user_data
        user_chat_id = update.message.chat.id
        selected_class = user_info.get("selected_class", "نامشخص")
        
        caption = (
            f"🔔 **ثبت‌نام جدید برای کلاس: {selected_class.replace('class_', '').capitalize()}**\n\n"
            f"👤 **نام:** {user_info.get('name', 'N/A')}\n"
            f"🎓 **شماره دانشجویی:** {user_info.get('student_id', 'N/A')}\n"
            f"📱 **شماره تماس:** {user_info.get('phone', 'N/A')}"
        )
        
        callback_data = f"approve_{user_chat_id}_{selected_class}"
        approval_button = InlineKeyboardMarkup([[InlineKeyboardButton("✅ تایید ثبت‌نام", callback_data=callback_data)]])
        
        media_group = [
            InputMediaPhoto(media=user_info.get("student_card_id"), caption=caption, parse_mode='Markdown'),
            InputMediaPhoto(media=payment_receipt_id)
        ]
        
        try:
            message_in_admin_group = await context.bot.send_media_group(chat_id=GROUP_CHAT_ID, media=media_group)
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID, 
                text="لطفا ثبت‌نام بالا را تایید یا رد کنید:", 
                reply_to_message_id=message_in_admin_group[0].message_id, 
                reply_markup=approval_button
            )
        except Exception as e:
            print(f"Error sending media group: {e}")

        context.user_data.clear()


# -- ثبت هندلرها --
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("cancel", cancel))

# --- هندلرهای جدید برای دکمه‌های دائمی ---
application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^شروع مجدد 🔄$"), start))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^لغو عملیات ❌$"), cancel))

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
    yield
    await application.stop()
    await application.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post("/")
async def handle_update(request: Request):
    body = await request.json()
    update = Update.de_json(body, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "FMCBot is running."}
