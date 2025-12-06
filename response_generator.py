import re
import random
from typing import Dict, List, Union
from external_api_mock import CustomerServiceAPI 

class ResponseGenerator:
    """
    Generates dynamic, randomized, and context-aware responses.
    Now distinguishes between 'Banking Issues' and 'General Conversation'.
    """

    def __init__(self, api_service: CustomerServiceAPI):
        self._api = api_service
        
        self._id_pattern = re.compile(r'\b(?:id|account|user|number)\s*(?:is|:)?\s*([a-zA-Z0-9]+)', re.IGNORECASE)

        # 1. Define Banking Keywords (To detect if the user is actually talking about business)
        self.banking_keywords = [
            "account", "login", "password", "money", "fund", "transfer", "transaction", 
            "bill", "credit", "debit", "card", "bank", "app", "website", "service", "locked"
        ]

        # 2. Define Response Templates
        self._response_templates = {
            "GREETING": [
                "Hello! How can I help you today?",
                "Hi there! I'm here to assist.",
                "Greetings! What's on your mind?"
            ],
            # --- TRANSACTIONAL RESPONSES (BANKING) ---
            "REQUEST_LOGIN_HELP": [
                "I can help with login. Please provide your **User ID**.",
                "Login trouble? No problem. What is your **User ID**?"
            ],
            "REQUEST_PAYMENT_INFO": [
                "I can pull up your billing details. Please type your **User ID**.",
                "Sure, let's look at your transactions. What is your **User ID**?"
            ],
            # --- EMOTIONAL / GENERAL RESPONSES (NON-BANKING) ---
            "EMPATHY_NEGATIVE": [
                "I'm sorry to hear that you're feeling this way.",
                "That sounds tough. I hope your day gets better.",
                "I'm here to listen if you want to tell me more.",
                "I understand. Is there anything specific causing this?",
                "I'm sorry. I know I'm just a bot, but I hope things improve for you."
            ],
            "GENERAL_CONVERSATION": [
                "I see. Tell me more about that.",
                "That's interesting.",
                "I understand.",
                "Okay, I'm listening."
            ],
            "COMPLAINT_TECHNICAL": [
                "I apologize for the service issue. Please provide your **User ID** so I can investigate.",
                "I understand your frustration with our service. Give me your **Account ID** and I'll fix it."
            ],
            "POSITIVE_FEEDBACK": [
                "That's great to hear!",
                "Awesome! Glad I could bring some positivity.",
                "Thanks! I appreciate the kind words."
            ],
            "THANK_YOU": [
                "You're welcome!",
                "Happy to help.",
                "Anytime!"
            ]
        }

    def _pick_random(self, key: str) -> str:
        options = self._response_templates.get(key, ["I didn't understand that."])
        return random.choice(options)

    def generate_response(self, user_input: str, intent: str, sentiment_label: str) -> str:
        """Generates response based on Context, Intent, and Sentiment."""
        
        # 1. ID Lookup Logic (Always Priority)
        match = self._id_pattern.search(user_input)
        user_id = match.group(1) if match else None

        if user_id:
            user_data = self._api.fetch_user_data(user_id)
            if user_data:
                return f"✅ Found account **{user_id}**. Status: {user_data['status']}."
            else:
                return f"🔍 ID **{user_id}** not found."

        # 2. CONTEXT CHECK: Is this a banking/service related query?
        # We check if the user mentioned any "business words" (money, login, account, etc.)
        is_banking_context = any(word in user_input.lower() for word in self.banking_keywords)

        # 3. Handle Negative Sentiment / Complaints
        if sentiment_label == "Negative" or intent == "COMPLAINT":
            if is_banking_context:
                # If they mentioned "bank/money/login", assume it's a technical complaint
                return self._pick_random("COMPLAINT_TECHNICAL")
            else:
                # If NO banking words, it's just a human expression ("I feel bad")
                return self._pick_random("EMPATHY_NEGATIVE")

        # 4. Handle Specific Intents
        if intent in self._response_templates:
            return self._pick_random(intent)

        # 5. General Fallback
        if sentiment_label == "Positive":
            return self._pick_random("POSITIVE_FEEDBACK")
        
        return self._pick_random("GENERAL_CONVERSATION")