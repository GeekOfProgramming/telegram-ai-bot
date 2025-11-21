import os
import sys
import chromadb  # <--- اضافه شد برای تنظیمات
from chromadb.config import Settings # <--- اضافه شد

# --- IMPORTS ---
try:
    from langchain_community.document_loaders import PyPDFLoader
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
PDF_FILE_PATH = "data.pdf"
MODEL_NAME = "llama3" 

# متغیر سراسری
retrieval_chain = None

def initialize_ai():
    global retrieval_chain
    print("🔄 در حال راه‌اندازی هوش مصنوعی (لطفا کمی صبر کنید)...")

    if not os.path.exists(PDF_FILE_PATH):
        print(f"❌ فایل {PDF_FILE_PATH} پیدا نشد!")
        return False

    try:
        # 1. Load
        loader = PyPDFLoader(PDF_FILE_PATH)
        docs = loader.load()

        # 2. Split
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # 3. Vector Store (با تنظیمات خاموش کردن Telemetry)
        # این بخش باعث می‌شود آن ارورهای قرمز دیگر نیایند
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=OllamaEmbeddings(model=MODEL_NAME),
            client_settings=Settings(anonymized_telemetry=False) 
        )
        retriever = vectorstore.as_retriever()

        # 4. LLM & Chain
        llm = ChatOllama(model=MODEL_NAME)
        
        system_prompt = (
            "You are a helpful assistant. Answer based on the context provided. "
            "Context:\n{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        print("✅ هوش مصنوعی با موفقیت لود شد! آماده پاسخگویی.")
        return True
        
    except Exception as e:
        print(f"❌ خطا در لود کردن هوش مصنوعی: {e}")
        return False

def get_answer_from_my_ai(user_question):
    global retrieval_chain
    
    # اگر هنوز لود نشده بود
    if retrieval_chain is None:
        success = initialize_ai()
        if not success:
            return "خطا: سیستم هنوز آماده نیست یا فایل مشکل دارد."

    try:
        response = retrieval_chain.invoke({"input": user_question})
        return response["answer"]
    except Exception as e:
        return f"خطا در پاسخگویی: {str(e)}"

if __name__ == "__main__":
    initialize_ai()