import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from fastapi import FastAPI
from pydantic import BaseModel
import my_brain # فایل جدید مغز
from contextlib import asynccontextmanager

# این تابع باعث می‌شود وقتی سرور روشن شد، اول هوش مصنوعی لود شود
@asynccontextmanager
async def lifespan(app: FastAPI):
    # کدهای قبل از شروع سرور
    my_brain.initialize_ai() 
    yield
    # کدهای موقع خاموش شدن (اگر لازم بود)

app = FastAPI(lifespan=lifespan)

# تعریف مدل داده‌ای که از سمت بات می‌آید
# ما توافق کردیم که بات یک JSON بفرستد به شکل: {"question": "..."}
class UserInput(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"Status": "Server is Online 🟢"}

@app.post("/chat")
async def chat_endpoint(input_data: UserInput):
    print(f"📩 یک درخواست جدید رسید: {input_data.question}") # لاگ در ترمینال سرور
    
    # ارسال سوال به تابع هوش مصنوعی
    ai_response = my_brain.get_answer_from_my_ai(input_data.question)
    
    # برگرداندن جواب به بات تلگرام
    return {"answer": ai_response}