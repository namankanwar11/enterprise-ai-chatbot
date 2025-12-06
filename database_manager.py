import sqlite3
from typing import Dict, List, Tuple

class DatabaseManager:
    """
    Manages SQLite database with Thread-Safe connections.
    Now supports retrieving history and saving Intents.
    """

    def __init__(self, db_name="chatbot_analysis.db"):
        self.db_name = db_name
        self._create_tables() 

    def _get_connection(self):
        """Establishes a new, temporary connection."""
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def _create_tables(self):
        """Creates tables. Updated to include INTENT in messages."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Added 'intent' column to this table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                speaker TEXT NOT NULL,
                text TEXT NOT NULL,
                intent TEXT, 
                sentiment_label TEXT,
                compound_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                overall_sentiment TEXT,
                trend_summary TEXT
            )
        """)
        conn.commit()
        conn.close()

    def insert_message(self, session_id: str, speaker: str, text: str, intent: str = None, sentiment_data: Dict = None):
        """Inserts a message. Now accepts INTENT."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        label = sentiment_data.get('label') if sentiment_data else None
        score = sentiment_data.get('compound_score') if sentiment_data else None
        
        cursor.execute("""
            INSERT INTO messages 
            (session_id, speaker, text, intent, sentiment_label, compound_score) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, speaker, text, intent, label, score))
        
        conn.commit()
        conn.close() 

    def insert_session_summary(self, session_id: str, start_time: str, end_time: str, overall_sentiment: str, trend_summary: str):
        """Inserts the final session summary."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions 
            (session_id, start_time, end_time, overall_sentiment, trend_summary) 
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, start_time, end_time, overall_sentiment, trend_summary))
        conn.commit()
        conn.close()

    # --- NEW HISTORY FEATURES ---

    def get_all_sessions(self):
        """Fetches a list of all past sessions for the sidebar."""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Get most recent sessions first
        cursor.execute("SELECT session_id, start_time, overall_sentiment FROM sessions ORDER BY start_time DESC")
        data = cursor.fetchall()
        conn.close()
        return data

    def get_messages_for_session(self, session_id: str):
        """Fetches all messages for a specific session to reload chat."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT speaker, text, intent, sentiment_label, compound_score FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
        data = cursor.fetchall()
        conn.close()
        return data