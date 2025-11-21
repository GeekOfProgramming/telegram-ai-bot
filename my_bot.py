import logging
import httpx
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- تنظیمات ---
BOT_TOKEN = "8257891887:AAHW7KhSVsPGtDuq77BgHKtevDq8tIHyDeE"
AI_API_URL = "http://127.0.0.1:8000/chat"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- 🎨 طراحی منوها (UI) ---

def main_menu_keyboard():
    keyboard = [
        ["🧠 مشاوره هوشمند (پرسش آزاد)"],
        ["📚 خدمات ما", "❓ سوالات متداول"],
        ["☎️ پشتیبانی انسانی", "🇮🇹 درباره کلاب"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def ai_mode_keyboard():
    keyboard = [
        ["🔙 بازگشت به منوی اصلی"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def faq_keyboard():
    keyboard = [
        ["💰 بورسیه استانی (DSU)", "📅 ددلاین دانشگاه‌ها"],
        ["📄 مدارک ویزا", "🏠 وضعیت خوابگاه"],
        ["🔙 بازگشت به منوی اصلی"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- 🧠 اتصال به سرور ---

async def query_custom_ai(user_question, user_id):
    async with httpx.AsyncClient() as client:
        try:
            # ارسال تایپینگ طولانی برای حس زنده بودن
            response = await client.post(
                AI_API_URL,
                json={"question": user_question, "user_id": user_id},
                timeout=100.0 
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("answer", "❌ پاسخی دریافت نشد.")
            else:
                return f"⚠️ خطا در سرور: {response.status_code}"
        except httpx.RequestError:
            return "🔌 سرور هوشمند در حال بروزرسانی است. لطفا دقایقی دیگر تلاش کنید."
        except Exception as e:
            return f"خطای ناشناخته: {str(e)}"

# --- 📝 هندلرها (Logic) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ai_mode'] = False
    user_name = update.effective_user.first_name
    
    welcome_msg = (
        f"🇮🇹 **سلام {user_name} عزیز! به ایتالیا اجوکیشن کلاب خوش اومدی** 👋\n\n"
        "من دستیار هوشمند شما در مسیر مهاجرت تحصیلی هستم. "
        "اینجا همه چیز درباره تحصیل در ایتالیا رو پیدا می‌کنی.\n\n"
        "👇 **چطور میتونم کمکت کنم؟**"
    )
    
    await update.message.reply_text(welcome_msg, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user_mode = context.user_data.get('ai_mode', False)

    # --- دکمه‌های اصلی ---
    
    if text == "🔙 بازگشت به منوی اصلی":
        context.user_data['ai_mode'] = False
        await update.message.reply_text("🏠 به منوی اصلی برگشتیم.", reply_markup=main_menu_keyboard())
        return

    elif text == "🧠 مشاوره هوشمند (پرسش آزاد)":
        context.user_data['ai_mode'] = True
        msg = (
            "🤖 **حالت مشاوره هوشمند فعال شد!**\n\n"
            "من تمام فایل‌های راهنما، اکسل رشته‌ها و PDFهای کلاب رو خوندم. "
            "میتونی به **فارسی** یا **انگلیسی** هر سوالی داری بپرسی.\n\n"
            "💡 *مثال‌هایی برای پرسیدن:*\n"
            "🔸 _ددلاین دانشگاه تورین برای رشته معماری کی هست؟_\n"
            "🔸 _برای بورسیه استانی چه مدارکی لازم دارم؟_\n"
            "🔸 _شهریه دانشگاه پادووا چقدره؟_\n\n"
            "✍️ **سوالت رو تایپ کن:**"
        )
        await update.message.reply_text(msg, reply_markup=ai_mode_keyboard(), parse_mode="Markdown")
        return

    elif text == "❓ سوالات متداول":
        msg = "🧐 **سوالات پرتکرار دانشجویان**\nروی موضوع مورد نظرت کلیک کن:"
        await update.message.reply_text(msg, reply_markup=faq_keyboard(), parse_mode="Markdown")
        return

    elif text == "📚 خدمات ما":
        services = (
            "💎 **خدمات VIP ایتالیا اجوکیشن کلاب:**\n\n"
            "1️⃣ مشاوره انتخاب رشته و دانشگاه\n"
            "2️⃣ نگارش حرفه‌ای SOP و CV\n"
            "3️⃣ ثبت‌نام بورسیه استانی (تضمینی)\n"
            "4️⃣ خدمات ویزا و شبیه‌سازی مصاحبه سفارت\n\n"
            "📩 برای رزرو وقت مشاوره، دکمه «پشتیبانی انسانی» رو بزن."
        )
        await update.message.reply_text(services, parse_mode="Markdown")
        return
        
    elif text == "☎️ پشتیبانی انسانی":
        contact = (
            "👩‍💻 **ارتباط با ادمین‌های کلاب**\n\n"
            "اگر سوال خیلی خاصی داری یا میخوای وقت مشاوره بگیری، به آیدی زیر پیام بده:\n\n"
            "🆔 @YourAdminID\n"
            "🌐 Website: www.italyeducationclub.com"
        )
        await update.message.reply_text(contact, parse_mode="Markdown")
        return
        
    elif text == "🇮🇹 درباره کلاب":
        about = (
            "🏛 **درباره ما**\n\n"
            "ما تیمی از دانشجویان و فارغ‌التحصیلان دانشگاه‌های برتر ایتالیا (Polimi, Unipd, Sapienza) هستیم. "
            "هدف ما حذف واسطه‌های غیرضروری و ارائه اطلاعات شفاف و رایگان به دانشجویان ایرانیه."
        )
        await update.message.reply_text(about, parse_mode="Markdown")
        return

    # --- دکمه‌های بخش سوالات متداول (بدون AI) ---
    elif text == "💰 بورسیه استانی (DSU)":
        await update.message.reply_text("✅ **بورسیه استانی:** شامل غذای رایگان، خوابگاه رایگان و سالانه حدود 7000 یورو کمک هزینه نقدی است که بر اساس عدد ایزه (ISEE) خانواده تعلق میگیره.", parse_mode="Markdown")
        return
    elif text == "📅 ددلاین دانشگاه‌ها":
        await update.message.reply_text("⏰ **ددلاین‌ها:** اکثر دانشگاه‌ها از نوامبر/دسامبر اپلیکیشن رو باز میکنن. ددلاین تورین و میلان معمولا زودتره. برای تاریخ دقیق اسم دانشگاه رو به هوش مصنوعی بگو.", parse_mode="Markdown")
        return
    elif text == "📄 مدارک ویزا":
        await update.message.reply_text("🛂 **مدارک مهم ویزا:** پذیرش دانشگاه، نامه تمکن مالی، گردش حساب، اجاره‌نامه (یا رزرو هتل) و بیمه مسافرتی.", parse_mode="Markdown")
        return

    # --- مدیریت پیام در حالت AI ---
    if user_mode:
        await update.message.reply_chat_action(action="typing")
        
        # دریافت پاسخ
        ai_response = await query_custom_ai(text, user_id)
        
        # قالب‌بندی خوشگل پاسخ
        formatted_reply = (
            f"🎓 **پاسخ مشاور:**\n\n"
            f"{ai_response}\n\n"
            f"──────────────\n"
            f"💭 _اگر سوال دیگه‌ای داری بپرس، یا دکمه بازگشت رو بزن._"
        )
        await update.message.reply_text(formatted_reply, parse_mode="Markdown")
    
    else:
        # اگر دکمه‌ای نبود و حالت AI هم نبود
        await update.message.reply_text("⚠️ متوجه نشدم. لطفا از دکمه‌های منو استفاده کن یا گزینه «مشاوره هوشمند» رو بزن.")

# --- اجرا ---
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    print("Italy Education Bot is running with New UI...")
    application.run_polling()