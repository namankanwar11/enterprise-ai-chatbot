from transformers import pipeline
import streamlit as st

# Cache the model so it doesn't reload every time
@st.cache_resource
def load_summarizer():
    # 'sshleifer/distilbart-cnn-12-6' is a faster, lighter version of BART
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

class SummarizerEngine:
    """
    Summarizes the conversation content into a concise paragraph.
    """
    def __init__(self):
        self.summarizer = load_summarizer()

    def summarize_chat(self, messages: list) -> str:
        """
        Combines user/bot messages and generates a summary.
        """
        if not messages:
            return "No conversation to summarize."

        # 1. Prepare the transcript text
        # We only take the last ~1000 words to keep it fast and within model limits
        transcript = ""
        for msg in messages:
            sender = msg['speaker']
            text = msg['text']
            transcript += f"{sender}: {text}\n"

        if len(transcript) < 50:
            return "Conversation too short to summarize."

        # 2. Run Summarization
        try:
            # max_length=150 ensures a concise summary
            summary_list = self.summarizer(transcript, max_length=150, min_length=30, do_sample=False)
            return summary_list[0]['summary_text']
        except Exception as e:
            return f"Summarization unavailable: {e}"