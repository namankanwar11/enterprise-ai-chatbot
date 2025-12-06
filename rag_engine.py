import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import streamlit as st

# --- FIX: Define this function OUTSIDE the class ---
@st.cache_resource
def load_embedding_model():
    """Loads the model once and caches it globally."""
    return SentenceTransformer('all-MiniLM-L6-v2')

class RAGEngine:
    """
    Handles PDF ingestion and vector search for Retrieval Augmented Generation.
    Uses a local embedding model (free/fast) to understand text.
    """
    def __init__(self):
        # Load the model using the standalone cached function
        self.model = load_embedding_model()
        self.index = None
        self.chunks = []

    def ingest_pdf(self, uploaded_file):
        """Reads PDF, splits text into chunks, and builds a search index."""
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # Simple chunking by sentence/paragraph (approx 200 chars)
        raw_chunks = text.split('. ')
        self.chunks = [chunk.strip() for chunk in raw_chunks if len(chunk) > 20]
        
        if not self.chunks:
            return False

        # Create Embeddings
        embeddings = self.model.encode(self.chunks)
        
        # Build Vector Index (FAISS)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        return True

    def search(self, query: str, top_k=2) -> str:
        """Searches the document for the best matching text."""
        if self.index is None or not self.chunks:
            return None
            
        # Encode query
        query_vector = self.model.encode([query]).astype('float32')
        
        # Search index
        distances, indices = self.index.search(query_vector, top_k)
        
        # Threshold: If distance is too high (weak match), ignore it
        if distances[0][0] > 1.5: 
            return None
            
        # Combine top results
        # Check to ensure indices are valid
        valid_results = []
        for i in indices[0]:
            if 0 <= i < len(self.chunks):
                valid_results.append(self.chunks[i])
                
        if not valid_results:
            return None

        return " ... ".join(valid_results)