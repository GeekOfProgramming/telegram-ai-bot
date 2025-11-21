import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import time
import httpx

# تنظیمات لاگ برای دیباگ کردن
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- تنظیمات و توکن ---
BOT_TOKEN = "8257891887:AAHW7KhSVsPGtDuq77BgHKtevDq8tIHyDeE"

# --- شبیه‌سازی تابع اتصال به هوش مصنوعی ---
# --- تنظیمات آدرس سرور هوش مصنوعی ---
# فعلا روی لوکال هاست تنظیم شده. بعدا که رفتی روی کلاد، این آدرس عوض میشه
AI_API_URL = "http://127.0.0.1:8000/chat" 

async def query_custom_ai(user_question):
    """
    این تابع متن کاربر را به API هوش مصنوعی می‌فرستد و جواب را می‌گیرد.
    """
    async with httpx.AsyncClient() as client:
        try:
            # ارسال درخواست POST به سرور هوش مصنوعی
            # Timeout را روی 30 ثانیه می‌گذاریم چون مدل‌های AI ممکن است کند باشند
            response = await client.post(
                AI_API_URL,
                json={"question": user_question},
                timeout=300.0 
            )
            
            # اگر پاسخ موفقیت‌آمیز بود (کد 200)
            if response.status_code == 200:
                data = response.json()
                return data.get("answer", "پاسخی دریافت نشد.")
            else:
                return f"خطا در ارتباط با سرور: {response.status_code}"
                
        except httpx.RequestError as e:
            return "متاسفانه سرور هوش مصنوعی در دسترس نیست. لطفا بعدا تلاش کنید."
        except Exception as e:
            return f"یک خطای غیرمنتظره رخ داد: {str(e)}"

# --- توابع هندلر (Handlers) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی کاربر استارت می‌زند یا به منوی اصلی برمی‌گردد"""
    
    # ریست کردن حالت هوش مصنوعی
    context.user_data['ai_mode'] = False
    
    # تعریف دکمه‌های کیبورد
    keyboard = [
        ["🤖 سوال از هوش مصنوعی"],
        ["📚 درباره پروژه", "📞 تماس با ما"],
        ["❓ راهنما"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "سلام! به بات دستیار خوش آمدید.\nلطفا یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت تمام پیام‌های متنی"""
    text = update.message.text
    user_mode = context.user_data.get('ai_mode', False)

    # 1. بررسی دکمه‌های منوی اصلی
    if text == "🤖 سوال از هوش مصنوعی":
        context.user_data['ai_mode'] = True
        
        # دکمه بازگشت برای خروج از حالت AI
        keyboard = [["🔙 بازگشت به منوی اصلی"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "حالت هوش مصنوعی فعال شد! 🧠\n\nهر سوالی بپرسید، توسط مدل هوشمند پاسخ داده می‌شود.\nبرای خروج دکمه بازگشت را بزنید.",
            reply_markup=reply_markup
        )
        return

    elif text == "🔙 بازگشت به منوی اصلی":
        await start(update, context)
        return

    elif text == "📚 درباره پروژه":
        await update.message.reply_text("این پروژه بخشی از تحقیقات مهندسی اطلاعات حمید لطفعلیان است.")
        return

    elif text == "📞 تماس با ما":
        await update.message.reply_text("ایمیل: example@email.com\nتلگرام: @username")
        return

    elif text == "❓ راهنما":
        await update.message.reply_text("شما می‌توانید از دکمه‌ها برای پیمایش استفاده کنید.")
        return

    # 2. اگر دکمه خاصی نبود، بررسی می‌کنیم آیا در حالت AI هستیم؟
    if user_mode:
        # --- اینجا جایی است که به هوش مصنوعی وصل می‌شویم ---
        await update.message.reply_chat_action(action="typing") # نمایش حالت تایپینگ
        
        ai_response = await query_custom_ai(text)
        
        await update.message.reply_text(f"🤖: {ai_response}")
    else:
        # اگر در حالت AI نبود و دکمه‌ای هم نزد
        await update.message.reply_text("متوجه نشدم. لطفا از دکمه‌های منو استفاده کنید.")

# --- بدنه اصلی برنامه ---
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # هندلر دستور استارت
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # هندلر پیام‌های متنی (همه متن‌ها به این تابع می‌روند)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(msg_handler)
    
    print("Bot is running...")
    application.run_polling()