import os
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters
)

# --- بخش تنظیمات ---

# متغیرهای محیطی از Render خوانده می‌شوند
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# شناسه عددی گروه ادمین‌ها
GROUP_CHAT_ID = -4881825561

# لینک گوگل شیت برای لیست کلاس‌ها
SHEET_LINK = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit?usp=sharing"

# لینک گروه‌های کلاسی
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

# آیدی‌های پشتیبانی
SUPPORT_IDS = {
    "piano_sup": ("سرپرست پیانو", "@piano_admin_id"),
    "guitar_sup": ("سرپرست گیتار", "@guitar_admin_id"),
    "violin_sup": ("سرپرست کمانچه و ویولن", "@violin_admin_id"),
    "tonbak_sup": ("سرپرست دف و تنبک", "@tonbak_admin_id"),
    "solfege1_sup": ("سرپرست سلفژ مقدماتی", "@solfege1_admin_id"),
    "solfege2_sup": ("سرپرست سلفژ پیشرفته", "@solfege2_admin_id"),
    "vocal_sup": ("سرپرست آواز", "@vocal_admin_id"),
    "dotar_sup": ("سرپرست دوتار", "@dotar_admin_id"),
    "setar_sup": ("سرپرست تار و سه‌تار", "@setar_admin_id"),
    "santoor_sup": ("سرپرست سنتور", "@santoor_admin_id"),
    "deputy_sup": ("دبیر کانون", "@deputy_admin_id"),
}

# --- ساخت برنامه اصلی ربات ---
application = ApplicationBuilder().token(BOT_TOKEN).build()

# -- کیبورد و پیام‌های اصلی --
main_reply_keyboard = ReplyKeyboardMarkup([["شروع مجدد 🔄", "لغو عملیات ❌"]], resize_keyboard=True)
welcome_text = "سلام! به ربات کانون موسیقی خوش آمدید 🎶\nاز طریق دکمه‌های زیر می‌تونید به بخش‌های مختلف دسترسی داشته باشید."
faq_text = """
**سوالات متداول ❔**

**۱. کلاس‌ها کجا برگزار می‌شوند؟**
در ساختمان مجتمع کانون‌های فرهنگی هنری دانشگاه.

**۲. اگر غیبت کنیم چه می‌شود؟**
جلسات جبرانی برای غیبت هنرجو برگزار نخواهد شد.

**۳. آیا امکان بازگشت وجه وجود دارد؟**
فقط در صورت انصراف پیش از جلسه اول، ۸۰٪ وجه بازگردانده می‌شود. پس از آن بازگشت وجه ممکن نیست.
"""
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

# --- دکمه‌های شیشه‌ای منوی اصلی (اصلاح شده) ---
menu_buttons = [
    [InlineKeyboardButton("🎼 ثبت نام کارگاه های موسیقی", callback_data="register")],
    [InlineKeyboardButton("🎹 رزرو تمرین ساز", callback_data="reserve")],
    # --- این خط اصلاح شد ---
    [InlineKeyboardButton("📖 نشریه ارغنون", url="https://t.me/Ferdowsi_Music_Club/2154")],
    [InlineKeyboardButton("📋 لیست کلاس‌ها و وضعیت", callback_data="class_list")],
    [InlineKeyboardButton("❔ سوالات متداول", callback_data="faq")],
    [InlineKeyboardButton("🛠️ پشتیبانی", callback_data="support")],
]

# --- دکمه‌های کلاس‌ها برای ثبت‌نام (اصلاح شده) ---
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

# --- توابع اصلی ربات ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(welcome_text, reply_markup=main_reply_keyboard)
    await update.message.reply_text("لطفا یک گزینه را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(menu_buttons))

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("عملیات لغو شد.", reply_markup=main_reply_keyboard)
    await start(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data.startswith("approve_") or data.startswith("reject_"):
        try:
            action, student_chat_id, class_name = data.split("_", 2)
            student_chat_id = int(student_chat_id)
            admin_name = query.from_user.first_name

            if action == "approve":
                group_link = CLASS_LINKS.get(class_name)
                if group_link:
                    msg = "🎉 ثبت‌نام شما در کارگاه موسیقی تایید شد!\n\nلطفاً از طریق لینک زیر وارد گروه کلاس خود شوید:"
                    btn = [[InlineKeyboardButton("ورود به گروه کلاس", url=group_link)]]
                    await context.bot.send_message(chat_id=student_chat_id, text=msg, reply_markup=InlineKeyboardMarkup(btn))
                    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ توسط {admin_name} تایید شد", callback_data="done")]]))
                else:
                    await query.answer("خطا: لینک گروه برای این کلاس تعریف نشده است.", show_alert=True)
            
            elif action == "reject":
                msg = "⚠️ متاسفانه ثبت‌نام شما تایید نشد. لطفاً پس از رفع مشکل، مجدداً اقدام فرمایید یا با پشتیبانی تماس بگیرید."
                await context.bot.send_message(chat_id=student_chat_id, text=msg)
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"❌ توسط {admin_name} رد شد", callback_data="done")]]))

        except Exception as e:
            print(f"Error in approval/rejection callback: {e}")
            await query.answer("خطایی در پردازش رخ داد.", show_alert=True)
        return

    if data == "register":
        await query.edit_message_text("لطفاً یک کارگاه انتخاب کنید:", reply_markup=InlineKeyboardMarkup(register_buttons))
    elif data == "class_list":
        await query.edit_message_text(
            "برای مشاهده لیست کلاس‌ها، ظرفیت‌ها و برنامه‌ زمانی، به لینک گوگل شیت زیر مراجعه کنید:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("مشاهده لیست کلاس‌ها 📋", url=SHEET_LINK)]])
        )
    elif data == "faq":
        await query.edit_message_text(faq_text, parse_mode='Markdown')
    elif data == "support":
        support_buttons = [[InlineKeyboardButton(name, callback_data=f"sup_{key}")] for key, (name, _) in SUPPORT_IDS.items()]
        await query.edit_message_text("پشتیبانی مورد نظر را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(support_buttons))
    elif data.startswith("sup_"):
        key = data.split("_", 1)[1]
        _, admin_id = SUPPORT_IDS.get(key, ("نامشخص", "یافت نشد"))
        await query.edit_message_text(f"آیدی پشتیبان: {admin_id}")
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
    # --- این بخش حذف شد چون دیگر لازم نیست ---
    # elif data == "journal":
    #     ...

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await update.message.reply_text("شماره دانشجویی مورد قبول نیصت. لطفا مجددا وارد کنید.")
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
    step = context.user_data.get("step")
    if step == "student_card":
        context.user_data["student_card_id"] = update.message.photo[-1].file_id
        context.user_data["step"] = "payment"
        await update.message.reply_text(payment_text)
    elif step == "payment":
        payment_receipt_id = update.message.photo[-1].file_id
        await update.message.reply_text("""✅ ثبت‌نام اولیه شما با موفقیت انجام شد. اطلاعات شما برای بررسی به شورای کانون ارسال گردید. متشکرم!""", reply_markup=main_reply_keyboard)

        user_info = context.user_data
        user_chat_id = update.message.chat.id
        selected_class = user_info.get("selected_class", "نامشخص")
        
        caption = (
            f"🔔 **ثبت‌نام جدید برای کلاس: {selected_class.replace('class_', '').capitalize()}**\n\n"
            f"👤 **نام:** {user_info.get('name', 'N/A')}\n"
            f"🎓 **شماره دانشجویی:** {user_info.get('student_id', 'N/A')}\n"
            f"📱 **شماره تماس:** {user_info.get('phone', 'N/A')}\n"
        )
        
        callback_approve = f"approve_{user_chat_id}_{selected_class}"
        callback_reject = f"reject_{user_chat_id}_{selected_class}"
        approval_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ تایید", callback_data=callback_approve),
                InlineKeyboardButton("❌ رد", callback_data=callback_reject)
            ]
        ])
        
        media_group = [
            InputMediaPhoto(media=user_info.get("student_card_id"), caption=caption, parse_mode='Markdown'),
            InputMediaPhoto(media=payment_receipt_id)
        ]
        
        try:
            admin_messages = await context.bot.send_media_group(chat_id=GROUP_CHAT_ID, media=media_group)
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID, 
                text="لطفا ثبت‌نام بالا را تایید یا رد کنید:", 
                reply_to_message_id=admin_messages[0].message_id, 
                reply_markup=approval_buttons
            )
        except Exception as e:
            print(f"Error sending media group: {e}")

        context.user_data.clear()

# -- ثبت هندلرها --
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("cancel", cancel))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^شروع مجدد 🔄$"), start))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^لغو عملیات ❌$"), cancel))
application.add_handler(CallbackQueryHandler(handle_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^شروع مجدد 🔄$") & ~filters.Regex("^لغو عملیات ❌$"), handle_message))
application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))

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
