import streamlit as st
import pandas as pd
import uuid
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from datetime import datetime
import traceback
import io

# Import modules
from database_manager import DatabaseManager
from sentiment_analyzer import SentimentAnalyzer 
from response_generator import ResponseGenerator
from intent_classifier import IntentClassifier
from external_api_mock import CustomerServiceAPI 
from rag_engine import RAGEngine 
from report_generator import generate_pdf 
from admin_dashboard import show_admin_dashboard 
from content_moderation import ContentModerator
from translation_engine import TranslationEngine 
from summarizer_engine import SummarizerEngine # 🆕 NEW IMPORT

# --- HELPER: VOICE TO TEXT ---
def transcribe_audio(audio_bytes):
    r = sr.Recognizer()
    audio_data = sr.AudioData(audio_bytes, 44100, 2) 
    try:
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return None
    except Exception as e:
        return f"Error: {e}"

# --- INITIALIZATION ---
def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
        st.session_state.analyzer = SentimentAnalyzer()
        st.session_state.classifier = IntentClassifier()
        st.session_state.api_service = CustomerServiceAPI() 
        st.session_state.generator = ResponseGenerator(st.session_state.api_service)
        st.session_state.rag_engine = RAGEngine() 
        st.session_state.moderator = ContentModerator()
        st.session_state.translator = TranslationEngine() 
        st.session_state.summarizer = SummarizerEngine() # 🆕 INIT SUMMARIZER
        
        st.session_state.last_processed_audio = None 
        start_new_session()
        st.session_state.initialized = True

def start_new_session():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.start_time = datetime.now()
    st.session_state.messages = [] 
    st.session_state.user_compound_scores = [] 
    st.session_state.final_analysis_done = False
    st.session_state.user_input = ""
    st.session_state.last_processed_audio = None
    
    intro = st.session_state.generator.generate_response("", "GREETING", "Neutral")
    st.session_state.messages.append({
        "speaker": "Chatbot", 
        "text": intro, 
        "intent": "N/A", 
        "sentiment": "Neutral", 
        "display_text": intro
    })

def process_user_input(user_input_raw: str):
    try:
        target_lang_code = st.session_state.get('current_lang_code', 'en')
        
        if target_lang_code != 'en':
            user_input_eng = st.session_state.translator.translate(user_input_raw, 'en')
        else:
            user_input_eng = user_input_raw

        # Safety Check
        if not st.session_state.moderator.is_safe(user_input_eng):
            violation_msg_eng = "⚠️ I cannot answer this question. It violates our safety guidelines."
            violation_msg_display = st.session_state.translator.translate(violation_msg_eng, target_lang_code)
            
            st.session_state.messages.append({
                "speaker": "User", "text": user_input_eng, 
                "intent": "BLOCKED_CONTENT", "sentiment": "Negative", "score": -0.99,
                "display_text": user_input_raw
            })
            st.session_state.db_manager.insert_message(
                st.session_state.session_id, "User", user_input_eng, "BLOCKED_CONTENT", {'label': 'Negative', 'compound_score': -0.99}
            )
            st.session_state.messages.append({
                "speaker": "Chatbot", "text": violation_msg_eng, 
                "intent": "SAFETY_REFUSAL", "sentiment": "Neutral",
                "display_text": violation_msg_display
            })
            st.session_state.db_manager.insert_message(
                st.session_state.session_id, "Chatbot", violation_msg_eng, "SAFETY_REFUSAL", None
            )
            return

        # RAG
        rag_context = ""
        if st.session_state.rag_engine.index is not None:
            found_text = st.session_state.rag_engine.search(user_input_eng)
            if found_text:
                rag_context = f"\n\n[RAG Source]: ...{found_text}..."

        # Analyze
        intent = st.session_state.classifier.classify(user_input_eng)
        sentiment_data = st.session_state.analyzer.analyze_statement(user_input_eng)
        sentiment_label = sentiment_data['label']
        score = sentiment_data['compound_score']
        st.session_state.user_compound_scores.append(score)
        
        st.session_state.messages.append({
            "speaker": "User", "text": user_input_eng, 
            "intent": intent, "sentiment": sentiment_label, "score": score,
            "display_text": user_input_raw
        })
        st.session_state.db_manager.insert_message(
            st.session_state.session_id, "User", user_input_eng, intent, sentiment_data
        )

        # Generate Response
        bot_response_eng = st.session_state.generator.generate_response(user_input_eng, intent, sentiment_label)
        if rag_context:
            bot_response_eng += rag_context

        if target_lang_code != 'en':
            bot_response_display = st.session_state.translator.translate(bot_response_eng, target_lang_code)
        else:
            bot_response_display = bot_response_eng

        st.session_state.messages.append({
            "speaker": "Chatbot", "text": bot_response_eng, 
            "intent": "N/A", "sentiment": "Neutral",
            "display_text": bot_response_display
        })
        st.session_state.db_manager.insert_message(
            st.session_state.session_id, "Chatbot", bot_response_eng, "RESPONSE", None
        )
        
    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()

def handle_submit():
    if st.session_state.input_text and not st.session_state.final_analysis_done:
        user_input = st.session_state.input_text
        st.session_state.input_text = "" 
        process_user_input(user_input)

# --- UI ---
def main():
    st.set_page_config(page_title="Global Enterprise AI", layout="wide")
    initialize_session_state()

    with st.sidebar:
        st.title("⚙️ Control Panel")
        mode = st.radio("Mode", ["Chat Interface", "Admin Dashboard"])
        st.divider()
        
        if mode == "Chat Interface":
            st.subheader("🌐 Language")
            lang_options = list(st.session_state.translator.supported_languages.keys())
            selected_lang = st.selectbox("Select Language", lang_options, index=0)
            st.session_state.current_lang_code = st.session_state.translator.get_lang_code(selected_lang)
            st.info("🔊 Audio available for all messages.")

            st.divider()
            uploaded_file = st.file_uploader("Upload Policy PDF (RAG)", type=['pdf'])
            if uploaded_file:
                with st.spinner("Indexing..."):
                    if st.session_state.rag_engine.ingest_pdf(uploaded_file):
                        st.success("Indexed!")

            st.divider()
            if st.button("➕ New Chat", type="primary"):
                start_new_session()
                st.rerun()
            
            # History
            sessions = st.session_state.db_manager.get_all_sessions()
            if sessions:
                st.caption("Recent History:")
            for s_id, start_time, sentiment in sessions[:5]:
                 lbl = f"{start_time[:10]} ({sentiment.split('-')[0]})"
                 if st.button(lbl, key=s_id):
                     st.session_state.session_id = s_id
                     st.session_state.messages = []
                     st.session_state.user_compound_scores = []
                     st.session_state.final_analysis_done = True
                     
                     history = st.session_state.db_manager.get_messages_for_session(s_id)
                     for sp, txt, intt, sent, sc in history:
                        st.session_state.messages.append({
                            "speaker": sp, "text": txt, "intent": intt, "sentiment": sent, "score": sc,
                            "display_text": txt 
                        })
                     st.rerun()

    if mode == "Admin Dashboard":
        show_admin_dashboard(st.session_state.db_manager)
    
    else: 
        st.title("🤖 Global Enterprise AI Chatbot")
        
        chat_container = st.container(height=500)
        with chat_container:
            for i, msg in enumerate(st.session_state.messages):
                with st.chat_message(msg["speaker"]):
                    display_content = msg.get("display_text", msg["text"])
                    st.write(display_content)
                    
                    if msg["speaker"] == "User":
                        if msg.get("intent") == "BLOCKED_CONTENT":
                            st.caption("🚨 Content Flagged as Unsafe")
                        else:
                            st.caption(f"Intent: {msg['intent']} | Sentiment: {msg['sentiment']}")
                    
                    if msg["speaker"] == "Chatbot":
                        lang_code = st.session_state.get('current_lang_code', 'en')
                        audio_fp = st.session_state.translator.text_to_speech_audio(display_content, lang_code)
                        if audio_fp:
                            st.audio(audio_fp, format="audio/mp3", start_time=0)

        if not st.session_state.final_analysis_done:
            col_input, col_mic = st.columns([6, 1])
            with col_input:
                ph = "Type message..."
                if st.session_state.get('current_lang_code') == 'hi': ph = "Sandesh type karein..."
                st.chat_input(ph, key="input_text", on_submit=handle_submit)
            
            with col_mic:
                st.write("Voice:")
                audio = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='recorder', format="wav", use_container_width=True)
                if audio:
                    if audio['bytes'] != st.session_state.last_processed_audio:
                        st.session_state.last_processed_audio = audio['bytes']
                        text = transcribe_audio(audio['bytes'])
                        if text:
                            st.success(f"Heard: {text}") 
                            process_user_input(text)
                            st.rerun()

            if st.button("End Session & Analyze"):
                st.session_state.final_analysis_done = True
                st.rerun()

        if st.session_state.final_analysis_done:
            st.divider()
            scores = st.session_state.user_compound_scores
            if not scores and st.session_state.messages:
                 scores = [m['score'] for m in st.session_state.messages if m['speaker'] == 'User' and m['score'] is not None]

            if scores:
                # 1. Standard Analysis
                label, sentiment_summary = st.session_state.analyzer.analyze_conversation(scores)
                trend = st.session_state.analyzer.summarize_trend(scores)
                
                # 2. 🆕 AI CONTENT SUMMARY
                with st.spinner("🧠 AI is summarizing the conversation..."):
                    content_summary = st.session_state.summarizer.summarize_chat(st.session_state.messages)

                st.subheader("📊 Session Report")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"**Sentiment:** {sentiment_summary}")
                with col_b:
                    st.success(f"**AI Summary:** {content_summary}")
                
                st.write(f"**Trend:** {trend}")
                st.line_chart(pd.DataFrame(scores, columns=['Sentiment Score']))

                # Pass the AI Summary to the PDF generator as well
                pdf_bytes = generate_pdf(st.session_state.session_id, st.session_state.messages, f"{sentiment_summary}\n\nAI Content Summary: {content_summary}", trend)
                st.download_button("📥 Download PDF Report", pdf_bytes, f"report_{st.session_state.session_id}.pdf", "application/pdf")
            else:
                st.warning("No data to analyze.")

if __name__ == "__main__":
    main()