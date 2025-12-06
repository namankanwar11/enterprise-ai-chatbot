import os
import numpy as np
import torch
from transformers import pipeline
from typing import Dict, List, Tuple

class SentimentAnalyzer:
    """
    Handles sentiment analysis using a Hugging Face Transformer model (RoBERTa).
    This provides much higher accuracy and better context understanding than VADER.
    """
    
    MODEL_NAME = "siebert/sentiment-roberta-large-english"

    def __init__(self):
        # Optimization: Suppress excessive tokenizers warning
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Streamlit tends to re-initialize classes, so we use a simple memoization 
        # check to avoid re-loading the large model unnecessarily.
        if not hasattr(self, '_classifier') or self._classifier is None:
            print(f"Loading Transformer model: {self.MODEL_NAME}...")
            
            try:
                self._classifier = pipeline(
                    "sentiment-analysis", 
                    model=self.MODEL_NAME, 
                    device=0 if torch.cuda.is_available() else -1,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                print("Model loaded successfully.")
            except Exception as e:
                print(f"Error loading model: {e}")
                # Use SystemExit to prevent app from running without the core tool
                raise SystemExit("Failed to load Transformer model. Check installations (transformers, torch).")

    def analyze_statement(self, text: str) -> Dict[str, float]:
        """
        Tier 2: Performs statement-level analysis.
        Returns a dict with 'label' and 'compound_score'.
        """
        result = self._classifier(text)[0]
        
        # Standardize the output to match the original structure (label and score)
        return {
            'label': result['label'].capitalize(),
            # Map score: POSITIVE -> 0 to 1, NEGATIVE -> -1 to 0
            'compound_score': result['score'] if result['label'] == 'POSITIVE' else -result['score']
        }

    def analyze_conversation(self, scores: List[float]) -> Tuple[str, str]:
        """
        Tier 1: Calculates the overall sentiment using the average compound score.
        """
        if not scores:
            return "Neutral", "No user input analyzed."
        
        average_compound = np.mean(scores)
        label = self.get_label(average_compound)
        
        summary = ""
        if average_compound > 0.15:
            summary = "General satisfaction and strong positive engagement observed."
        elif average_compound < -0.15:
            summary = "General dissatisfaction, potential for unresolved issues."
        else:
            summary = "Sentiment is mostly stable or weakly positive/negative."
            
        return label, summary
    
    def summarize_trend(self, scores: List[float]) -> str:
        """
        Tier 2 Enhancement: Summarise trend or shift in mood.
        """
        if len(scores) < 2:
            return "Trend summary requires at least two user messages."

        first_score = scores[0]
        last_score = scores[-1]
        change = last_score - first_score

        if change > 0.4:
            return "Mood Shift: Significant improvement (e.g., concern was quickly resolved)."
        elif change < -0.4:
            return "Mood Shift: Significant deterioration (e.g., frustration increased dramatically)."
        elif abs(change) > 0.15:
             return "Mood Trend: Minor shift, stable overall but noticed a change."
        else:
            return "Mood Trend: Very stable sentiment throughout the exchange."

    def get_label(self, score: float) -> str:
        """Converts the compound score to a simple label."""
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"