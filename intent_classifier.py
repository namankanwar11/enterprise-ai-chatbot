import re
from typing import Dict, List

class IntentClassifier:
    """Classifies the user's message into a specific intent using keyword matching."""

    def __init__(self):
        self._intent_patterns: Dict[str, List[str]] = {
            "GREETING": ["hello", "hi", "hey", "good morning"],
            "COMPLAINT": ["disappoint", "frustrat", "upset", "problem", "issue", "bad", "wrong"],
            "REQUEST_LOGIN_HELP": ["login", "access", "password", "account", "lock", "can't get in"],
            "REQUEST_PAYMENT_INFO": ["pay", "bill", "invoice", "charge", "refund", "cost"],
            "THANK_YOU": ["thank", "cheers", "appreciate", "thanks"],
            "GOODBYE": ["bye", "see you", "exit", "stop"]
        }
        
    def classify(self, text: str) -> str:
        """Processes the text and returns the most probable intent."""
        lower_text = text.lower()

        # Check for specific intents using pattern matching
        for intent, patterns in self._intent_patterns.items():
            for pattern in patterns:
                # Use regex word boundaries (\b) for better matching accuracy
                if re.search(r'\b' + re.escape(pattern) + r'\b', lower_text):
                    return intent
        
        # Fallback intent
        return "GENERAL_QUERY"