import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from database_manager import DatabaseManager

def show_admin_dashboard(db_manager: DatabaseManager):
    st.header("📊 Admin Analytics Dashboard")
    
    conn = db_manager._get_connection()
    try:
        df_msgs = pd.read_sql("SELECT * FROM messages", conn)
    except Exception as e:
        st.error(f"Database Error: {e}")
        conn.close()
        return
    conn.close()
    
    if df_msgs.empty:
        st.warning("No chat data found. Start a conversation to see metrics!")
        return

    # --- METRICS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Messages", len(df_msgs))
    col2.metric("Active Conversations", df_msgs['session_id'].nunique())
    
    if 'sentiment_label' in df_msgs.columns:
        neg_count = df_msgs[df_msgs['sentiment_label'] == 'Negative'].shape[0]
        col3.metric("Negative Flags", neg_count)
    
    st.divider()
    
    # --- ☁️ WORD CLOUD (NEW) ---
    st.subheader("🔥 Hot Topics (Word Cloud)")
    
    # Combine all user text into one big string
    user_text = " ".join(df_msgs[df_msgs['speaker'] == 'User']['text'].astype(str).tolist())
    
    if user_text:
        # Generate Cloud
        wordcloud = WordCloud(width=800, height=300, background_color='black', colormap='Pastel1').generate(user_text)
        
        # Display using Matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        # Set background to match Streamlit dark theme roughly
        fig.patch.set_facecolor('#0e1117') 
        st.pyplot(fig)
    else:
        st.info("Not enough data for Word Cloud.")

    st.divider()

    # --- CHARTS ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Intent Distribution")
        if 'intent' in df_msgs.columns:
            clean = df_msgs[df_msgs['intent'].notna() & (df_msgs['intent'] != "N/A")]
            if not clean.empty:
                counts = clean['intent'].value_counts().reset_index()
                counts.columns = ['Intent', 'Count']
                fig = px.pie(counts, values='Count', names='Intent', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("Message Volume")
        if 'timestamp' in df_msgs.columns:
            df_msgs['date'] = pd.to_datetime(df_msgs['timestamp']).dt.date
            daily = df_msgs.groupby('date').size().reset_index(name='count')
            fig = px.bar(daily, x='date', y='count')
            st.plotly_chart(fig, use_container_width=True)