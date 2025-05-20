# search.py

import webbrowser
import re

def web_search(cmd: str) -> str:
    # Arama anahtar kelimesini çıkartalım
    keywords = re.sub(r"(google'da|internette|webde|arama yap|ara)", "", cmd, flags=re.IGNORECASE).strip()
    
    if not keywords:
        return "Ne aramamı istersin? Örnek: 'Google'da yapay zeka nedir'"

    url = f"https://www.google.com/search?q={keywords.replace(' ', '+')}"
    webbrowser.open(url)
    return f"🔍 Google'da şunu arıyorum: {keywords}"
