# news.py

import feedparser

# RSS kaynakları (isteğe göre çoğaltılabilir)
RSS_FEEDS = {
    "NTV": "https://www.ntv.com.tr/rss",
    "BBC Türkçe": "https://www.bbc.com/turkce/index.xml",
    "Hürriyet": "https://www.hurriyet.com.tr/rss/anasayfa"
}

def get_news(max_items=5):
    try:
        news_list = []
        for source, url in RSS_FEEDS.items():
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
            news_list.append(f"📰 {source}")
            for entry in feed.entries[:max_items]:
                title = entry.get("title", "Başlık yok")
                link = entry.get("link", "")
                news_list.append(f"- {title}\n  {link}")
            news_list.append("")  # boş satır
        return "\n".join(news_list) if news_list else "🔍 Şu an haberler alınamıyor."
    except Exception as e:
        return f"❌ Haberler alınırken bir hata oluştu: {str(e)}"

# Fonksiyonu dışa aktar
__all__ = ['get_news']
