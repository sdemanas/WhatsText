import os
import unicodedata
import re

from better_profanity import profanity

def sanitize_text(text: str) -> str:
    """
    Normalizes Unicode, strips control characters, and trims trailing whitespace.
    Redacts profanity from the text.

    Args: 
        text (str): The raw input string.
    
    Returns: 
        str: NFKC-normalized text with unified line endings.
    """
    # Initialize profanity cleaner
    profanity.load_censor_words()

    text = unicodedata.normalize("NFKC", text)
    cleaned = []
    for ch in text:
        if ch in ("\n", "\t"):
            cleaned.append(ch)
            continue

        cat = unicodedata.category(ch)
        if cat not in ("Cc", "Cf"):
            cleaned.append(ch)

    text = profanity.censor("".join(cleaned), '*')

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Trim trailing spaces
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    return text

def sanitize_file(file_path: str) -> str:
    """
    Processes file content through sanitize_text and saves to a new path.

    Args: 
        file_path (str): Path to the source UTF-8 file.

    Returns: 
        str: Path to the generated '*_sanitized' file.

    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    clean = sanitize_text(raw)

    dirpath, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)

    out_path = os.path.join(dirpath, f"{name}_sanitized{ext}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(clean)

    return out_path
