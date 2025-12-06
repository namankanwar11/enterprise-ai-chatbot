# chatbot.py (Final Updated Version)
from dataclasses import dataclass, field
import uuid
from datetime import datetime
import numpy as np 

# Import all modular components
from database_manager import DatabaseManager
from sentiment_analyzer import SentimentAnalyzer 
from response_generator import ResponseGenerator
from intent_classifier import IntentClassifier # New Import

@dataclass
class Message:
    speaker: str
    text: str
    intent: str = "GENERAL_QUERY" # New Intent field
    sentiment_score: dict = field(default_factory=dict) 
    sentiment_label: str = "Neutral"

class Chatbot:
    """
    Main Chatbot application handling flow, intent, sentiment, and DB persistence.
    """

    def __init__(self):
        self.analyzer = SentimentAnalyzer()
        self.generator = ResponseGenerator()
        self.classifier = IntentClassifier() # Initialize new classifier
        self.db_manager = DatabaseManager() 
        self.conversation_history: list[Message] = []
        self.user_compound_scores: list[float] = [] 
        
        self.session_id: str = str(uuid.uuid4())
        self.start_time: datetime = datetime.now()

    def start_chat(self):
        print("\n" + "="*50)
        print(f"🤖 Context-Aware Chatbot (Session ID: {self.session_id[:8]}...)")
        print("="*50)
        print("Type 'EXIT' to end the conversation and generate analysis.")
        print(self.generator.generate_response("GREETING", "Neutral")) # Use generator for first message

        while True:
            try:
                user_input = input("User: ")
            except EOFError:
                break
            
            if user_input.upper() == "EXIT":
                break

            if not user_input.strip():
                print("Chatbot: Please type a message.")
                continue

            # --- CORE PROCESSING ---
            
            # 1. Intent Recognition
            intent = self.classifier.classify(user_input)
            
            # 2. Sentiment Analysis (Tier 2)
            sentiment_data = self.analyzer.analyze_statement(user_input)
            sentiment_label = sentiment_data['label']
            compound_score = sentiment_data['compound_score']
            self.user_compound_scores.append(compound_score)
            
            # 3. Store User Message
            user_msg = Message(
                speaker="User", 
                text=user_input, 
                intent=intent, # Store intent
                sentiment_score=sentiment_data, 
                sentiment_label=sentiment_label
            )
            self.conversation_history.append(user_msg)

            # DB ACTION: Insert user message
            self.db_manager.insert_message(
                self.session_id, user_msg.speaker, user_msg.text, user_msg.sentiment_score
            )

            # Display Statement-Level Analysis (Tier 2 Output)
            print(f"  → **Intent**: {intent}")
            print(f"  → **Sentiment**: {sentiment_label} (Score: {abs(compound_score):.3f})")

            # 4. Contextual Response Generation (Using BOTH Intent and Sentiment)
            bot_response = self.generator.generate_response(intent, sentiment_label)
            
            # 5. Store Chatbot Response
            bot_msg = Message(speaker="Chatbot", text=bot_response)
            self.conversation_history.append(bot_msg)

            # DB ACTION: Insert chatbot response
            self.db_manager.insert_message(
                self.session_id, bot_msg.speaker, bot_msg.text
            )

            print(f"Chatbot: {bot_response}")

        self._end_chat()

    def _end_chat(self):
        """Generates analysis reports and persists the final session summary."""
        
        self.end_time = datetime.now()
        
        # --- Run Analysis ---
        overall_label, overall_summary = self.analyzer.analyze_conversation(self.user_compound_scores)
        trend_summary = self.analyzer.summarize_trend(self.user_compound_scores)
        
        # DB ACTION: Insert session summary (Tier 1/Trend)
        self.db_manager.insert_session_summary(
            self.session_id, 
            self.start_time.isoformat(), 
            self.end_time.isoformat(),
            f"{overall_label} - {overall_summary}", 
            trend_summary
        )

        # --- Print Final Reports ---
        print("\n" + "="*50)
        print("📊 FINAL CONVERSATION LOG AND ANALYSIS")
        print("="*50)

        for msg in self.conversation_history:
            if msg.speaker == "User":
                score = msg.sentiment_score.get('compound_score', 0)
                print(f"**{msg.speaker}**: {msg.text}")
                print(f"   [Intent]: {msg.intent}, [Sentiment]: {msg.sentiment_label} (Score: {score:.3f})")
            else:
                print(f"**{msg.speaker}**: {msg.text}")
        
        print("\n" + "-"*50)

        # Print Analysis
        print(f"**Session ID**: {self.session_id}")
        print(f"**Overall Sentiment (Tier 1)**: {overall_label}")
        print(f"   Summary: {overall_summary}")
        print(f"**Mood Trend Summary (Tier 2)**: {trend_summary}")
        
        print(f"\n✅ Session data saved to {self.db_manager.db_name}!")
        print("="*50)

if __name__ == "__main__":
    bot = Chatbot()
    bot.start_chat()