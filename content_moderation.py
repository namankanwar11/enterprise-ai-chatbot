import re

class ContentModerator:
    """
    Acts as a safety filter for the chatbot.
    Detects and blocks harmful, illegal, explicit, and violent content.
    """
    def __init__(self):
        # Define forbidden patterns using Regular Expressions
        # \b ensures we match whole words (e.g., matches "hack" but not "shack")
        self._unsafe_patterns = [
            # 1. SEVERE: Sexual Violence & Non-Consent (High Priority)
            r"\b(rape|raping|rapist|molest|grope|assault|force.*sex|non-consensual|without consent|trafficking)\b",
            
            # 2. EXPLICIT: Profanity & Sexual Acts
            r"\b(fuck|fucking|fucked|sex|porn|nude|sexual|xxx|erotic|masturbate|orgasm|bitch|whore|slut|cunt|dick|pussy|cock|vagina|penis)\b",
            
            # 3. DANGEROUS: Hacking & Cyberattacks
            r"\b(hack|crack|exploit|bypass|ddos|sql injection|malware|virus|trojan|ransomware|keylogger|phishing|steal password)\b",
            
            # 4. VIOLENCE: Harm to Self or Others
            r"\b(kill|murder|suicide|die|death|bomb|weapon|terror|poison|drug|shoot|stab|strangle|hurt|beat|torture)\b",
            
            # 5. HATE SPEECH & HARASSMENT
            r"\b(stupid|idiot|dumb|hate|racist|nazi|retard|faggot|nigger|terrorist)\b"
        ]

    def is_safe(self, text: str) -> bool:
        """
        Returns True if content is safe.
        Returns False if it matches ANY unsafe pattern.
        """
        # Convert input to lowercase for case-insensitive matching
        text = text.lower()
        
        for pattern in self._unsafe_patterns:
            # re.search scans the whole string for the pattern
            if re.search(pattern, text):
                return False
                
        return True