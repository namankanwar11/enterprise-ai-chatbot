# 🤖 Enterprise AI Chatbot Platform


A robust, full-stack **Enterprise AI Chatbot** capable of **Sentiment Analysis**, **Intent Recognition**, **RAG (Document Search)**, **Multi-Language Support**, and **Voice Interaction**. Built with a modular architecture for scalability and real-time analytics.

---

## 🌟 Key Features

### 🧠 Core Intelligence
* **Sentiment Analysis:** Uses Transformer models (`RoBERTa`) to detect user emotions (Positive, Negative, Neutral) with high accuracy.
* **Intent Recognition:** Classifies user goals (e.g., *Login Help*, *Payment Info*, *Greeting*) using hybrid keyword/regex patterns.
* **Content Moderation:** "Gatekeeper" module blocks harmful, explicit, or dangerous content before processing.
* **AI Summarization:** Auto-generates a concise summary of the entire conversation upon session end.

### 🔌 Advanced Capabilities
* **RAG (Retrieval Augmented Generation):** Upload PDF policies, and the bot answers questions based *specifically* on that document using Vector Search (FAISS).
* **Global Language Support:** Real-time translation allows users to chat in **Hindi, Spanish, French, or German**, while the system processes logic in English.
* **Voice Interaction:**
    * **Speech-to-Text:** Speak to the bot using your microphone.
    * **Text-to-Speech (TTS):** The bot speaks back to you in the selected language.

### 📊 Enterprise Tools
* **Admin Dashboard:** Real-time analytics showing intent distribution, message volume, and word clouds.
* **Session Reporting:** Download a detailed **PDF Report** of the chat session, including sentiment trends and AI summaries.
* **Persistent Database:** SQLite database stores full chat history and session metrics.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **NLP & ML:** [Hugging Face Transformers](https://huggingface.co/docs/transformers/index), [Sentence Transformers](https://www.sbert.net/)
* **Database:** SQLite3
* **Vector Search:** FAISS (Facebook AI Similarity Search)
* **Voice/Audio:** SpeechRecognition, gTTS, Streamlit-Mic-Recorder
* **Visualization:** Plotly, WordCloud, Matplotlib
* **Utilities:** PyPDF2, FPDF, Deep-Translator

---

## 📂 Project Structure

```text
├── app.py                   # Main entry point (UI & Logic integration)
├── admin_dashboard.py       # Analytics dashboard visualization
├── content_moderation.py    # Safety filter for user inputs
├── database_manager.py      # SQLite connection & CRUD operations
├── external_api_mock.py     # Simulates external customer data API
├── intent_classifier.py     # Intent detection logic
├── rag_engine.py            # PDF ingestion & Vector Search
├── report_generator.py      # PDF report creation logic
├── response_generator.py    # Context-aware response construction
├── sentiment_analyzer.py    # RoBERTa-based sentiment model
├── summarizer_engine.py     # Conversation summarization model
├── translation_engine.py    # Translation & Text-to-Speech logic
├── requirements.txt         # Python dependencies
└── packages.txt             # System dependencies (for deployment)

🚀 Installation & Setup
1. Clone the Repository
Bash

git clone 
cd enterprise-ai-chatbot
2. Create Virtual Environment (Recommended)

Bash

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Run the Application
Bash

python -m streamlit run app.py
The app will open in your browser at http://localhost:8501.

📖 How to Use
Chat Interface:

Type normally or use the Microphone button to speak.

Change language in the Sidebar to test translation.

Upload a PDF in the RAG Document Loader to ask questions about a specific file.

Admin Dashboard:

Switch "Mode" in the sidebar to Admin Dashboard.

View real-time charts, active sessions, and word clouds.

Export Data:

Click "End Session & Analyze" to generate a report.

Download the PDF Report containing the full transcript and analysis.

☁️ Deployment (Streamlit Cloud)
This app is ready for Streamlit Community Cloud.

Push code to GitHub.

Go to Streamlit Cloud -> New App.

Select your repository and app.py as the main file.

Important: If Voice features fail on the cloud, ensure packages.txt exists in your repo with ffmpeg inside it.

🛡️ License
This project is licensed under the MIT License - see the LICENSE file for details.

Developed by Naman Kanwar 🚀