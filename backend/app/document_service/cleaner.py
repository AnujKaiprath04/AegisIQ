import re
import unicodedata


class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        """Sanitize raw document text, normalize unicode, and remove excessive whitespace."""
        if not text:
            return ""

        # 1. Normalize unicode (NFKD)
        text = unicodedata.normalize("NFKD", text)

        # 2. Strip null and non-printable control characters (preserve \n and \t)
        text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or not unicodedata.category(ch).startswith("C"))

        # 3. Standardize carriage returns to standard linefeeds
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 4. Collapse runs of horizontal spaces/tabs
        text = re.sub(r"[ \t]+", " ", text)

        # 5. Limit consecutive linefeeds to max 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
