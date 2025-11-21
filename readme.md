# 🤖 AI-Powered Hybrid Telegram Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange?style=for-the-badge)
![Ollama](https://img.shields.io/badge/AI-Ollama%20(Local)-black?style=for-the-badge)

A hybrid Telegram bot that seamlessly blends traditional menu-based navigation with a powerful, locally hosted AI assistant. The AI utilizes **RAG (Retrieval-Augmented Generation)** to answer specialized questions based on your custom PDF documents.

---

## 🌟 Features

* **Hybrid Interface:**
    * 📱 **Standard Mode:** Quick access buttons for general information (Contact, About, FAQ).
    * 🧠 **AI Mode:** A dedicated state for chatting with the LLM.
* **Local RAG Architecture:**
    * Processes and embeds your private `PDF` data locally using **ChromaDB**.
    * Uses **Ollama** (Llama3) for privacy-focused, offline inference.
* **Microservices Design:**
    * Separation of concerns between the Telegram Bot (Frontend) and the AI Engine (Backend API).

---

## 🏗️ Architecture

The project follows a clean client-server architecture:

1.  **User** interacts with the Telegram Bot.
2.  **Bot (Client)** forwards AI queries to the FastAPI Server via HTTP.
3.  **FastAPI (Server)** invokes the RAG pipeline (`my_brain.py`).
4.  **AI Engine** retrieves context from `data.pdf` and generates a response using Ollama.


## 🛠️ **Prerequisites**
Before you begin, ensure you have met the following requirements:

    Python 3.10+ installed.

    Ollama installed and running.

A Telegram Bot Token (from @BotFather).

## 🚀 **Installation**

**1. Clone & Setup Environment**

    # Clone the repository
    git clone [https://github.com/your-username/telegram-ai-bot.git](https://github.com/your-username/telegram-ai-bot.git)

    # Navigate to directory
    cd telegram-ai-bot

    # Create a virtual environment
    python -m venv .venv

    # Activate environment (Windows)
    .\.venv\Scripts\activate
    # Activate environment (Mac/Linux)
    source .venv/bin/activate

**2. Install Dependencies**

    pip install -r requirements.txt

**3. Pull the AI Model**
    We use Llama3 by default. Run this in your terminal:

        ollama pull llama3

**4. Configuration**
    1. Place your custom PDF file in the root directory and rename it to data.pdf.
    2. Open my_bot.py and replace BOT_TOKEN with your actual Telegram token.


## ▶️ **Usage Guide**
To run the system, you need to execute the Server and the Bot in two separate terminals.

**Terminal 1:** Start the AI Server

    # Make sure .venv is activated
    uvicorn server:app --reload

    Wait until you see: Application startup complete

**Terminal 2:** Start the Telegram Bot

    # Make sure .venv is activated
    python my_bot.py
    
    Now, open your bot in Telegram and click "🤖 سوال از هوش مصنوعی" to start chatting!


## 📂 Project Structure
    telegram-ai-bot/
    ├── .venv/               # Virtual Environment
    ├── data.pdf             # Your knowledge base (PDF)
    ├── my_bot.py            # Telegram Bot logic (Frontend)
    ├── server.py            # FastAPI Server (Backend)
    ├── my_brain.py          # RAG & LangChain logic
    ├── requirements.txt     # Python dependencies
    └── README.md            # Documentation

## 🤝 Contributing
Developed by Hamid Lotfalian. Feel free to submit issues or pull requests.

```mermaid
graph LR
    A[User] -- Telegram --> B(Telegram Bot)
    B -- HTTP Request --> C{FastAPI Server}
    C -- Context Retrieval --> D[(ChromaDB)]
    C -- Inference --> E[Ollama / Llama3]
    E --> C
    C --> B
    B --> A
