import pandas as pd
import re

def normalize_text(text):
    if pd.isna(text):
        return ""
    # Convert to string first (handles integers like zip codes)
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
