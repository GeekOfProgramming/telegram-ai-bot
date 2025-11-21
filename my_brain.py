import os
import sys
import json
import chromadb
from chromadb.config import Settings

# --- IMPORTS ---
try:
    from langchain_core.documents import Document 
    from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    from langchain_chroma import Chroma
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    sys.exit(1)

# --- تنظیمات ---
DATA_FOLDER = "knowledge_base"
MODEL_NAME = "qwen2.5:14b"

# متغیرهای سراسری
retrieval_chain = None
CHAT_HISTORY = {}

def load_documents_from_folder():
    """(خواندن تمام فایل‌ها با گزارش لحظه‌ای)"""
    documents = []
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return []
    
    files = os.listdir(DATA_FOLDER)
    print(f"📂 اسکن پوشه '{DATA_FOLDER}' ({len(files)} فایل پیدا شد)...")

    for file in files:
        file_path = os.path.join(DATA_FOLDER, file)
        try:
            # --- بخش جدید: خواندن JSON ---
            if file.endswith('.json'):
                print(f"   📋 در حال پردازش JSON: {file} ...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # تبدیل هر آیتم جیسون به یک سند متنی برای هوش مصنوعی
                    for item in data:
                        # فقط آیتم‌هایی که محتوا دارند را پردازش کن (دسته‌ها را رد کن)
                        if 'content' in item or 'description' in item:
                            # ساختن یک متن یکپارچه از تمام فیلدها
                            text_content = ""
                            if 'title' in item: text_content += f"Title: {item['title']}\n"
                            if 'description' in item: text_content += f"Description: {item['description']}\n"
                            if 'content' in item: text_content += f"Content: {item['content']}\n"
                            
                            # اضافه کردن سوالات متداول (FAQs) اگر وجود داشت
                            if 'faqs' in item and isinstance(item['faqs'], list):
                                text_content += "\nCommon Questions:\n"
                                for faq in item['faqs']:
                                    text_content += f"Q: {faq['q']}\nA: {faq['a']}\n"
                            
                            # اضافه کردن کلمات کلیدی برای سرچ بهتر
                            if 'keywords' in item and isinstance(item['keywords'], list):
                                text_content += f"\nKeywords: {', '.join(item['keywords'])}\n"

                            # ساخت آبجکت داکیومنت
                            new_doc = Document(page_content=text_content, metadata={"source": file, "title": item.get('title', 'Unknown')})
                            documents.append(new_doc)
            if file.endswith('.pdf'):
                print(f"   📄 در حال خواندن PDF: {file} ...")  # <--- اضافه شد
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif file.endswith('.csv'):
                print(f"   📊 در حال خواندن CSV: {file} ...")  # <--- اضافه شد
                try:
                    loader = CSVLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
                except:
                    loader = CSVLoader(file_path, encoding='cp1252')
                    documents.extend(loader.load())
            elif file.endswith('.txt'):
                print(f"   📝 در حال خواندن TXT: {file} ...")  # <--- اضافه شد
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
        except Exception as e:
            print(f"❌ خطا در فایل {file}: {e}")
    
    print(f"✅ تمام فایل‌ها خوانده شد. رفتن به مرحله ساخت دیتابیس...")
    return documents

def initialize_ai():
    global retrieval_chain
    print("🔄 در حال راه‌اندازی هوش مصنوعی...")
    
    try:
        docs = load_documents_from_folder()
        if not docs: return False

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)

        print("   🔨 در حال ساخت دیتابیس جدید...")
        
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=OllamaEmbeddings(model=MODEL_NAME),
            persist_directory="./chroma_db_json_v1",  
            client_settings=Settings(anonymized_telemetry=False) 
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        llm = ChatOllama(model=MODEL_NAME)
        
        # پرامپت جدید که تاریخچه چت را هم می‌فهمد
        system_prompt = (
            "You are a smart and helpful assistant for 'Italy Education Club'. "
            "Your goal is to answer the user's question using the provided Context."
            "\n\nGUIDELINES:"
            "\n1. **Trust the Context:** The text below contains valid facts. Use them to answer."
            "\n2. **Language:** Answer in PERSIAN (Farsi)."
            "\n3. **Be Helpful:** If the answer is in the context, explain it fully."
            "\n4. **Fallback:** Only if you absolutely cannot find the answer in the context, say exactly this:"
            "\n'متاسفانه در فایل‌های من اطلاعات دقیقی نبود. 😔\nلطفا برای راهنمایی دقیق‌تر به ادمین پیام دهید: 👇\n🆔 @YourAdminID'"
            "\n\nContext:\n{context}"
            "\n\nChat History:\n{chat_history}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        print("✅ هوش مصنوعی آماده است!")
        return True
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def get_chat_history_str(user_id):
    """تبدیل لیست پیام‌های قبلی کاربر به یک رشته متنی"""
    if user_id not in CHAT_HISTORY:
        return "No previous history."
    
    # فقط ۳ پیام آخر را برمی‌گردانیم تا حافظه شلوغ نشود
    recent_history = CHAT_HISTORY[user_id][-3:]
    return "\n".join(recent_history)

def update_chat_history(user_id, question, answer):
    """ذخیره سوال و جواب جدید در حافظه کاربر"""
    if user_id not in CHAT_HISTORY:
        CHAT_HISTORY[user_id] = []
    
    # فرمت ذخیره‌سازی: User: ... | AI: ...
    entry = f"User: {question} | AI: {answer}"
    CHAT_HISTORY[user_id].append(entry)

def get_answer_from_my_ai(user_question, user_id):
    global retrieval_chain

    print(f"🔍 [1] شروع پردازش سوال: {user_question}")

    if retrieval_chain is None:
        if not initialize_ai(): return "Error loading AI."

    # 1. دریافت تاریخچه این کاربر
    history_str = get_chat_history_str(user_id)

    try:
        print(f"🔍 [2] ارسال به مدل (این مرحله زمان‌بر است)...")
        # 2. ارسال سوال + تاریخچه به مدل
        response = retrieval_chain.invoke({
            "input": user_question,
            "chat_history": history_str # <--- ارسال تاریخچه به پرامپت
        })

        print(f"🔍 [3] جواب دریافت شد!")
        
        answer = response["answer"]
        
        # 3. آپدیت کردن حافظه برای سوال بعدی
        update_chat_history(user_id, user_question, answer)
        
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    initialize_ai()