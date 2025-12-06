from deep_translator import GoogleTranslator
from gtts import gTTS
import io

class TranslationEngine:
    """
    Handles translation and Text-to-Speech using in-memory streams.
    """
    def __init__(self):
        self.supported_languages = {
            "English": "en",
            "Hindi": "hi",
            "Spanish": "es",
            "French": "fr",
            "German": "de"
        }

    def get_lang_code(self, lang_name):
        return self.supported_languages.get(lang_name, "en")

    def translate(self, text: str, target_lang: str) -> str:
        if not text:
            return ""
        try:
            return GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            print(f"Translation Error: {e}")
            return text 

    def text_to_speech_audio(self, text: str, lang: str = 'en'):
        """
        Generates audio bytes in memory (no file saving).
        """
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            # Save to a memory buffer instead of a file
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            return fp
        except Exception as e:
            print(f"TTS Error: {e}")
            return None