import sqlite3
import pandas as pd

# Connect to the database file
conn = sqlite3.connect("chatbot_analysis.db")

print("--- 📊 SESSION REPORTS (Final Analysis) ---")
# Read the 'sessions' table
df_sessions = pd.read_sql_query("SELECT * FROM sessions", conn)
print(df_sessions)

print("\n--- 💬 INDIVIDUAL MESSAGES ---")
# Read the 'messages' table
df_messages = pd.read_sql_query("SELECT * FROM messages", conn)
print(df_messages.tail(5)) # Show last 5 messages

conn.close()