import logging import os import requests from telegram import Update, ChatPermissions from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters)

BOT_TOKEN = "7655902666:AAH-upyvDhkKBuZHRNejdv_BJLp0SmzSvHQ" OWNER_ID = 6950748024  # آیدی عددی شما

------------------------- لوگ ها -------------------------

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

---------------------- پاسخ کریتوسی ---------------------

def kratos_response(message: str) -> str: return f"من کریتوسم. و به این می‌گن حرف مفت: '{message}'\nسؤال بعدی."

------------------------- تولید تصویر -------------------------

def generate_image(prompt: str) -> str: url = "https://api-inference.huggingface.co/models/prompthero/openjourney" headers = {"Authorization": f"Bearer hf_your_huggingface_token"} payload = {"inputs": prompt} response = requests.post(url, headers=headers, json=payload) if response.status_code == 200: image_bytes = response.content path = "output.jpg" with open(path, 'wb') as f: f.write(image_bytes) return path return None

------------------------- تبدیل عکس به استایل ویدیوگیمی -------------------------

def stylize_image(image_path: str) -> str: url = "https://api.deepai.org/api/toonify" headers = {"api-key": "4a2a213f-737a-498c-be7c-a62d051c23a3"} with open(image_path, 'rb') as image_file: response = requests.post(url, files={'image': image_file}, headers=headers) if response.status_code == 200: output_url = response.json().get('output_url') return output_url return None

------------------------- کنترل اشتراک -------------------------

def is_premium(user_id: int) -> bool: return user_id == OWNER_ID

------------------------- خوش آمد -------------------------

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE): for member in update.message.new_chat_members: await update.message.reply_text(f"به قلمرو خشم، خوش آمدی {member.full_name}!")

------------------------- مدیریت پیام‌ها -------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.message.from_user.id text = update.message.text

if "عکس بساز" in text:
    if is_premium(user_id):
        prompt = text.replace("عکس بساز", "").strip()
        await update.message.reply_text("در حال ساخت تصویر... صبر کن.")
        path = generate_image(prompt)
        if path:
            await update.message.reply_photo(photo=open(path, 'rb'))
        else:
            await update.message.reply_text("مشکلی پیش اومد. دوباره امتحان کن.")
    else:
        await update.message.reply_text("برای استفاده از این قابلیت، باید مبلغی پرداخت کنی. شماره کارت: 6219861824919921")

elif "تبدیل کن به استایل بازی" in text and update.message.reply_to_message and update.message.reply_to_message.photo:
    if is_premium(user_id):
        photo = update.message.reply_to_message.photo[-1]
        photo_file = await photo.get_file()
        await photo_file.download_to_drive("input.jpg")
        await update.message.reply_text("در حال تبدیل تصویر به استایل بازی...")
        output_url = stylize_image("input.jpg")
        if output_url:
            await update.message.reply_photo(photo=output_url)
        else:
            await update.message.reply_text("مشکلی پیش اومد. دوباره امتحان کن.")
    else:
        await update.message.reply_text("این قابلیت ویژه کاربران اشتراکیه. کارت: 6219861824919921")

else:
    reply = kratos_response(text)
    await update.message.reply_text(reply)

------------------------- استارت -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("من کریتوسم. خدای جنگ. بپرس، تا پاسخ بدم.")

------------------------- اجرای اصلی -------------------------

if name == 'main': app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("ربات کریتوس آماده‌ست...")
app.run_polling()

