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


application = ApplicationBuilder().token(BOT_TOKEN).build()

# -- پیام‌ها و دکمه‌ها --
# ... (تمام پیام‌ها و دکمه‌های قبلی شما بدون تغییر اینجا قرار می‌گیرند) ...
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
    "💳 6219 8619 0605 4_INVALID_340\n"
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
]

# -- متدهای هندل --
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(menu_buttons))

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("فرآیند ثبت‌نام لغو شد.", reply_markup=ReplyKeyboardRemove())
    await start(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # --- بخش جدید: پردازش دکمه تایید ادمین ---
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
                # ویرایش پیام در گروه ادمین برای اطلاع‌رسانی
                admin_first_name = query.from_user.first_name
                await query.edit_message_caption(caption=query.message.caption + f"\n\n✅ **توسط {admin_first_name} تایید شد.**", parse_mode='Markdown')
            else:
                await query.edit_message_caption(caption=query.message.caption + "\n\n⚠️ **خطا: لینک گروه برای این کلاس تعریف نشده است.**", parse_mode='Markdown')

        except Exception as e:
            print(f"Error in
