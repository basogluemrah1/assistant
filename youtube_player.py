# youtube_player.py

import webbrowser
import re
import urllib.parse
import json
import requests
import random
import string

# Fonksiyonları dışa aktar
__all__ = ['search_youtube_videos', 'open_video_by_index', 'search_and_open_video']

last_video_links = []  # Seçim sistemi için dışarı açılan liste

def extract_videos_from_html(html_content):
    """HTML içeriğinden video bilgilerini çıkarır"""
    videos = []
    try:
        # videoId ve title için arama
        pattern = r'videoId":"(.*?)".*?"title":\{"runs":\[\{"text":"(.*?)"\}\]'
        matches = re.findall(pattern, html_content)
        
        # Her video için link ve başlık oluştur
        for i, (video_id, title) in enumerate(matches[:5]):  # Sadece ilk 5 video
            if video_id and title:
                link = f"https://www.youtube.com/watch?v={video_id}"
                videos.append({"title": title, "link": link})
    except Exception as e:
        print(f"Video çıkarma hatası: {e}")
    return videos

def search_youtube(query, limit=5):
    """YouTube araması yapar ve sonuçları döndürür"""
    # URL'yi hazırla
    search_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={search_query}"
    
    try:
        # User-Agent kullanarak bir tarayıcı gibi davran
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # YouTube sayfasını indir
        response = requests.get(url, headers=headers)
        html_content = response.text
        
        # HTML içeriğinden videoları çıkar
        videos = extract_videos_from_html(html_content)
        
        # Eğer hiç video bulunamadıysa URL'yi döndür
        if not videos:
            return url, []
            
        return url, videos
    except Exception as e:
        print(f"YouTube arama hatası: {e}")
        return url, []

def search_youtube_videos(cmd: str) -> str:
    global last_video_links
    
    # YouTube aç komutu kontrolü (direkt command içinde kontrol et)
    youtube_patterns = ["youtube aç", "youtube'u aç", "youtub aç", "yutub aç", "yutup aç"]
    for pattern in youtube_patterns:
        if pattern in cmd.lower():
            webbrowser.open("https://www.youtube.com")
            return "🎬 YouTube ana sayfası açılıyor..."
    
    # Normal YouTube araması için
    query = re.sub(r"(youtube'da|youtube|youtub|yutub|yutup)", "", cmd, flags=re.IGNORECASE).strip()
    
    # Sadece "aç" kaldıysa YouTube ana sayfasını aç
    if not query or query.lower() == "aç":
        webbrowser.open("https://www.youtube.com")
        return "🎬 YouTube ana sayfası açılıyor..."
    
    if not query:
        return "Ne aramamı istersin? Örnek: 'YouTube'da komik videolar aç'"
    
    try:
        # YouTube araması yap
        url, videos = search_youtube(query)
        
        # Sonuçlar boşsa doğrudan sayfayı aç
        if not videos:
            webbrowser.open(url)
            return f"🎬 YouTube'da '{query}' için arama sonuçları açılıyor..."
        
        # Sonuçları göster
        cevap = f"🎬 YouTube arama sonuçları ({query}):\n\n"
        last_video_links = []  # Listeyi temizle
        
        for i, video in enumerate(videos, start=1):
            title = video["title"]
            link = video["link"]
            cevap += f"{i}. {title}\n{link}\n\n"
            last_video_links.append(link)
            
        cevap += "Açmak için bir numara girin (örn: 1)."
        return cevap
    except Exception as e:
        # Hata durumunda doğrudan YouTube'u aç
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(search_url)
        return f"🎬 YouTube'da '{query}' için arama sonuçları açılıyor...\n(Not: {str(e)})"

def open_video_by_index(cmd: str) -> str:
    global last_video_links
    # Komuttan numarayı çıkar
    numbers = re.findall(r'\d+', cmd)
    if not numbers:
        return "Geçerli bir video numarası girmedin. Örnek: '1' veya '2'"
    
    index = int(numbers[0]) - 1
    
    # Geçerlilik kontrolü
    if not last_video_links:
        search_url = f"https://www.youtube.com/results"
        webbrowser.open(search_url)
        return "Son arama bulunamadı. YouTube ana sayfası açılıyor..."
    
    if 0 <= index < len(last_video_links):
        url = last_video_links[index]
        webbrowser.open(url)
        return f"🎥 {index+1}. video açılıyor..."
    else:
        return f"Geçerli bir numara girin (1-{len(last_video_links)} arası)"

def search_and_open_video(query: str) -> str:
    """Verilen sorguya göre YouTube'da arama yapar ve ilk videoyu açar"""
    if not query:
        return "Ne aramamı istersin? Örnek: 'YouTube'da komik videolar izle'"
    
    try:
        # YouTube araması yap
        _, videos = search_youtube(query)
        
        # Sonuçlar boşsa doğrudan arama sayfasını aç
        if not videos:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            return f"🎬 YouTube'da '{query}' için arama sonuçları açılıyor..."
        
        # İlk videoyu aç
        video = videos[0]
        webbrowser.open(video["link"])
        return f"🎥 '{video['title']}' videosu açılıyor..."
    except Exception as e:
        # Hata durumunda doğrudan YouTube aramasını aç
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(search_url)
        return f"🎬 YouTube'da '{query}' için arama sonuçları açılıyor...\n(Not: {str(e)})"
