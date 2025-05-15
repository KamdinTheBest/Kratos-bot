import logging
import os
import requests
from telegram import Update, ChatMemberUpdated, InputFile
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,
    ChatMemberHandler,
)
from openai import OpenAI

# تنظیمات اولیه لاگ‌ها
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# دریافت مقادیر از محیط
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

client = OpenAI(api_key=OPENAI_API_KEY)


# ——— پاسخ به چت با شخصیت کریتوس
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id

    try:
        # تولید پاسخ با OpenAI
        system_prompt = "تو کریتوس هستی. لحن صحبتت جدی، محکم و خشنه. فارسی صحبت کن و همیشه پاسخ بده."
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        response = completion.choices[0].message.content
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in AI response: {e}")
        await update.message.reply_text("یه مشکلی پیش اومد در پاسخ‌دادن.")

# ——— تولید تصویر با متن
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("دسترسی فقط برای مالک فعاله.")

    text = " ".join(context.args)
    if not text:
        return await update.message.reply_text("یک متن بده برای ساخت تصویر.")

    response = requests.post(
        "https://api.deepai.org/api/text2img",
        data={"text": text},
        headers={"api-key": DEEPAI_API_KEY},
    )
    image_url = response.json().get("output_url")
    if image_url:
        await update.message.reply_photo(photo=image_url)
    else:
        await update.message.reply_text("مشکلی در ساخت تصویر بود.")

# ——— تبدیل تصویر به سبک ویدیویی
async def stylize_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("فقط مالک بات می‌تونه از این استفاده کنه.")

    if not update.message.photo:
        return await update.message.reply_text("لطفاً یک عکس بفرست.")

    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    response = requests.post(
        "https://api.deepai.org/api/toonify",
        files={"image": photo_bytes},
        headers={"api-key": DEEPAI_API_KEY},
    )
    image_url = response.json().get("output_url")
    if image_url:
        await update.message.reply_photo(photo=image_url)
    else:
        await update.message.reply_text("پردازش تصویر موفق نبود.")

# ——— خوشامدگویی به اعضای جدید
async def welcome_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"به میدان نبرد خوش اومدی، {member.first_name}!")

# ——— دستور شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("من کریتوسم. منتظر فرمانتم.")

# ——— کنترل پیام‌های گروه (مثلاً حذف لینک یا پیام تبلیغاتی)
async def group_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "http" in text or "t.me/" in text:
        try:
            await update.message.delete()
            await update.message.reply_text("اینجا جای تبلیغ نیست!")
        except Exception as e:
            logger.warning(f"Couldn't delete message: {e}")

# ——— اجرای ربات
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("image", generate_image))
    app.add_handler(CommandHandler("stylize", stylize_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_moderation))

    logger.info("ربات کریتوس آماده‌ست...")
    await app.run_polling()

# ——— اجرا
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
