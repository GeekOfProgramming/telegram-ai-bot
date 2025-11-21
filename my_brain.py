import os
import sys
import chromadb
from chromadb.config import Settings

# --- IMPORTS ---
try:
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
MODEL_NAME = "phi3"

# متغیرهای سراسری
retrieval_chain = None
CHAT_HISTORY = {}  # <--- حافظه موقت کاربران: {user_id: ["Q:...", "A:..."]}

def load_documents_from_folder():
    """(خواندن تمام فایل‌ها)"""
    documents = []
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return []
    
    files = os.listdir(DATA_FOLDER)
    print(f"📂 اسکن پوشه '{DATA_FOLDER}'...")

    for file in files:
        file_path = os.path.join(DATA_FOLDER, file)
        try:
            if file.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif file.endswith('.csv'):
                try:
                    loader = CSVLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
                except:
                    loader = CSVLoader(file_path, encoding='cp1252')
                    documents.extend(loader.load())
            elif file.endswith('.txt'):
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
        except Exception as e:
            print(f"❌ خطا در فایل {file}: {e}")
    return documents

def initialize_ai():
    global retrieval_chain
    print("🔄 در حال راه‌اندازی هوش مصنوعی...")
    
    try:
        docs = load_documents_from_folder()
        if not docs: return False

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)

        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=OllamaEmbeddings(model=MODEL_NAME),
            client_settings=Settings(anonymized_telemetry=False) 
        )
        retriever = vectorstore.as_retriever()
        llm = ChatOllama(model=MODEL_NAME)
        
        # پرامپت جدید که تاریخچه چت را هم می‌فهمد
        system_prompt = (
            "You are an expert consultant for 'Italy Education Club'. "
            "Use the Context and Chat History to answer the student's question. "
            "If the answer is in the provided documents, give specific details. "
            "If you don't know, simply say you don't have that information."
            "\n\nIMPORTANT INSTRUCTION:"
            "\nALWAYS answer in the same language as the user's question."
            "\nIf the user asks in Persian (Farsi), you MUST answer in Persian."
            "\nIf the user asks in English, answer in English."
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
    
    if retrieval_chain is None:
        if not initialize_ai(): return "Error loading AI."

    # 1. دریافت تاریخچه این کاربر
    history_str = get_chat_history_str(user_id)

    try:
        # 2. ارسال سوال + تاریخچه به مدل
        response = retrieval_chain.invoke({
            "input": user_question,
            "chat_history": history_str # <--- ارسال تاریخچه به پرامپت
        })
        answer = response["answer"]
        
        # 3. آپدیت کردن حافظه برای سوال بعدی
        update_chat_history(user_id, user_question, answer)
        
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    initialize_ai()