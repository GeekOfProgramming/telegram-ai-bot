import os
import csv
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
import my_brain  # فایل مغز هوش مصنوعی

# --- تنظیمات لاگ ---
LOG_FILE = "chat_history.csv"

# --- خاموش کردن ارورهای قرمز ---
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# --- تابع ذخیره در اکسل ---
def log_interaction(question, answer):
    """
    این تابع سوال و جواب را به فایل اکسل اضافه می‌کند.
    از encoding='utf-8-sig' استفاده می‌کنیم تا حروف فارسی در اکسل درست نمایش داده شوند.
    """
    file_exists = os.path.isfile(LOG_FILE)
    
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            
            # اگر فایل تازه ساخته شده، اول تیتر ستون‌ها را بنویس
            if not file_exists:
                writer.writerow(["تاریخ (Date)", "ساعت (Time)", "سوال کاربر (Question)", "پاسخ هوش مصنوعی (Answer)"])
            
            # دریافت زمان فعلی
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            
            # نوشتن رکورد جدید
            writer.writerow([date_str, time_str, question, answer])
            print(f"💾 مکالمه در فایل {LOG_FILE} ذخیره شد.")
            
    except Exception as e:
        print(f"❌ خطا در ذخیره لاگ: {e}")

# --- لود کردن هوش مصنوعی در شروع برنامه ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # کدهای قبل از شروع سرور
    print("🚀 سرور در حال استارت است...")
    my_brain.initialize_ai()
    yield
    # کدهای موقع خاموش شدن
    print("🛑 سرور خاموش شد.")

app = FastAPI(lifespan=lifespan)

# مدل دیتای ورودی
class UserInput(BaseModel):
    question: str
    user_id: int

@app.get("/")
def read_root():
    return {"Status": "Italy Education AI Server is Online 🟢"}

@app.post("/chat")
async def chat_endpoint(input_data: UserInput):
    # 1. دریافت سوال
    user_q = input_data.question
    user_id = input_data.user_id  
    
    print(f"📩 درخواست جدید از کاربر {user_id}: {user_q}")
    
    # آیدی را به مغز می‌فرستیم تا حافظه را پیدا کند
    ai_response = my_brain.get_answer_from_my_ai(user_q, user_id)
    
    # لاگ کردن (اختیاری: می‌توانی آیدی را هم در اکسل ذخیره کنی)
    log_interaction(f"{user_id}: {user_q}", ai_response)
    
    # 4. ارسال پاسخ
    return {"answer": ai_response}