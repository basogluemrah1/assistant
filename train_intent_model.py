# train_intent_model.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import pickle

# 1. Eğitim verisi (komut, intent)
training_data = [
    # get_time (10 örnek)
    ("saat kaç", "get_time"),
    ("şu an saat kaç", "get_time"),
    ("zamanı göster", "get_time"),
    ("saat nedir", "get_time"),
    ("şimdi saat kaç oldu", "get_time"),
    ("bana zamanı söyler misin", "get_time"),
    ("saat", "get_time"),
    ("şu anki zaman", "get_time"),
    ("saat kaç oldu", "get_time"),
    ("zaman göster", "get_time"),
    
    # get_weather (10 örnek)
    ("hava durumu nasıl", "get_weather"),
    ("bugün hava nasıl", "get_weather"),
    ("hava sıcaklığı nedir", "get_weather"),
    ("hava raporu", "get_weather"),
    ("dışarıda hava nasıl", "get_weather"),
    ("yağmur var mı", "get_weather"),
    ("İstanbul'da hava", "get_weather"),
    ("ankara hava durumu", "get_weather"),
    ("yarın hava nasıl olacak", "get_weather"),
    ("bugün yağmur yağacak mı", "get_weather"),
    
    # calculate (20 örnek - daha çok matematiksel işlem çeşitliliği için)
    ("hesapla 5 + 2", "calculate"),
    ("5 çarpı 3 kaç eder", "calculate"),
    ("12 bölü 4 kaç", "calculate"),
    ("7 artı 8", "calculate"),
    ("15 eksi 7", "calculate"),
    ("123 + 456", "calculate"),
    ("2+2", "calculate"),
    ("100-25", "calculate"),
    ("50*4", "calculate"),
    ("81/9", "calculate"),
    ("kırk beş artı on", "calculate"),
    ("on iki çarpı altı", "calculate"),
    ("yüz bölü beş", "calculate"),
    ("yirmi eksi sekiz", "calculate"),
    ("hesapla 3.14*2", "calculate"),
    ("hesapla 2 üzeri 3", "calculate"),
    ("hesapla 5 faktöriyel", "calculate"),
    ("hesapla 7 mod 3", "calculate"),
    ("hesapla 2^5", "calculate"),
    ("hesapla 10 % 3", "calculate"),
    ("231232*3", "calculate"),
    ("500-250", "calculate"),
    ("45*12", "calculate"),
    ("1000/4", "calculate"),
    ("12+34+56", "calculate"),
    ("987-654", "calculate"),
    ("2*3*4", "calculate"),
    ("100/5/4", "calculate"),
    ("2^10", "calculate"),
    ("5!", "calculate"),
    ("10%3", "calculate"),
    
    # get_news (10 örnek)
    ("haberleri göster", "get_news"),
    ("bugünkü haberler", "get_news"),
    ("gündem nedir", "get_news"),
    ("son dakika haberleri", "get_news"),
    ("bugün ne olmuş", "get_news"),
    ("haberler neler", "get_news"),
    ("haberler", "get_news"),
    ("son haberler", "get_news"),
    ("haber", "get_news"),
    ("güncel haberler", "get_news"),
    
    # open_app (20 örnek - yaygın uygulamalar ve hatalı yazımlar)
    ("chrome'u aç", "open_app"),
    ("not defteri aç", "open_app"),
    ("word aç", "open_app"),
    ("excel aç", "open_app"),
    ("paint aç", "open_app"),
    ("hesap makinesi aç", "open_app"),
    ("krom aç", "open_app"),
    ("chrom aç", "open_app"),
    ("chorom aç", "open_app"),
    ("exploreri aç", "open_app"),
    ("chorme aç", "open_app"),
    ("spotify aç", "open_app"),
    ("steam aç", "open_app"),
    ("notepad aç", "open_app"),
    ("notpad aç", "open_app"),
    ("hesap makinesini aç", "open_app"),
    ("exel aç", "open_app"),
    ("vord aç", "open_app"),
    ("peyint aç", "open_app"),
    ("calculator aç", "open_app"),
    
    # open_file (10 örnek)
    ("belge.pdf dosyasını aç", "open_file"),
    ("pdf aç", "open_file"),
    ("döküman aç", "open_file"),
    ("dosya aç", "open_file"),
    ("sunum.pptx dosyasını aç", "open_file"),
    ("belge.docx dosyasını aç", "open_file"),
    ("excel.xlsx dosyasını aç", "open_file"),
    ("resim.jpg dosyasını aç", "open_file"),
    ("video.mp4 dosyasını aç", "open_file"),
    ("müzik.mp3 dosyasını aç", "open_file"),
    
    # exit (10 örnek)
    ("çıkış yap", "exit"),
    ("çıkış", "exit"),
    ("kapat", "exit"),
    ("görüşürüz", "exit"),
    ("programı kapat", "exit"),
    ("asistanı kapat", "exit"),
    ("çık", "exit"),
    ("exit", "exit"),
    ("by by", "exit"),
    ("kapatyt", "exit"),
    ("hoşçakal", "exit"),
    ("bitir", "exit"),
    ("sistemi kapat", "exit"),
    ("q", "exit"),
    ("güle güle", "exit"),

    # get_system_status (15 örnek)
    ("ram durumu", "get_system_status"),
    ("disk alanı", "get_system_status"),
    ("işlemci kullanımı", "get_system_status"),
    ("sistem durumu", "get_system_status"),
    ("bilgisayarım ısındı bir kontrol et", "get_system_status"),
    ("bilgisayarın performansını göster", "get_system_status"),
    ("boş alan ne kadar", "get_system_status"),
    ("pc takılıo bi kontrol et", "get_system_status"),
    ("pc nin durumunu göster", "get_system_status"),
    ("ram durumu göster", "get_system_status"),
    ("disk alanı kaç gb", "get_system_status"),
    ("işlemci kullanımı yüzde kaç", "get_system_status"),
    ("sistem sıcaklığı", "get_system_status"),
    ("bilgisayarımın performansı nasıl", "get_system_status"),
    ("pc'm yavaş mı çalışıyor", "get_system_status"),
    
    # web_search (15 örnek)
    ("google'da python nedir ara", "web_search"),
    ("internette haberler", "web_search"),
    ("ara: en iyi diziler", "web_search"),
    ("google'da arama yap", "web_search"),
    ("google'da bir konu hakkında araştırma yap", "web_search"),
    ("internetten bilgi bul", "web_search"),
    ("google'da makale bul", "web_search"),
    ("Google'da Python nedir ara", "web_search"),
    ("Internette son haberler", "web_search"),
    ("Ara: en iyi bilim kurgu filmleri", "web_search"),
    ("Google'da resim çizme teknikleri ara", "web_search"),
    ("Bul: COVID-19 aşısı hakkında bilgi", "web_search"),
    ("Internette iklim değişikliği etkileri", "web_search"),
    ("Google'da tarihin en büyük liderleri kimlerdir?", "web_search"),
    ("Ara: uzay keşifleri hakkında makaleler", "web_search"),
    
    # search_youtube (15 örnek)
    ("youtube'da komik videolar", "search_youtube"),
    ("youtube aç", "search_youtube"),
    ("youtube'da müzik ara", "search_youtube"),
    ("youtube video ara", "search_youtube"),
    ("youtube'da en iyi şiirler", "search_youtube"),
    ("youtube'da en iyi şarkılar", "search_youtube"),
    ("yutub'da eğlenceli video bul", "search_youtube"),
    ("yutub'da en iyi diziler", "search_youtube"),
    ("yutub'da en iyi filmler", "search_youtube"),
    ("youtup eğlenceli video bul", "search_youtube"),
    ("youtubeden eğlenceli video bul", "search_youtube"),
    ("yutup en iyi diziler", "search_youtube"),
    ("yutup en iyi filmler", "search_youtube"),
    ("yutup en iyi şarkılar", "search_youtube"),
    ("YouTube'da komik hayvan videoları oynat", "search_youtube"),
    
    # show_history (10 örnek)
    ("komut geçmişini göster", "show_history"),
    ("geçmişi aç", "show_history"),
    ("geçmiş", "show_history"),
    ("geçmişi", "show_history"),
    ("komut geçmişi", "show_history"),
    ("önceki komutlarımı göster", "show_history"),
    ("geçmişi göster", "show_history"),
    ("son komutlarım", "show_history"),
    ("önceki aramalarım", "show_history"),
    ("ne sordum", "show_history"),
    ("eski komutlar", "show_history"),
    ("komutlarımı göster", "show_history"),
    
    # open_folder (15 örnek - klasör açma varyasyonları)
    ("masaüstü klasörünü aç", "open_folder"),
    ("indirilenler klasörünü aç", "open_folder"),
    ("belgeler klasörünü aç", "open_folder"),
    ("resimler klasörünü aç", "open_folder"),
    ("müzikler klasörünü aç", "open_folder"),
    ("videolar klasörünü aç", "open_folder"),
    ("masaüstü aç", "open_folder"),
    ("indirilenler aç", "open_folder"),
    ("belgeler aç", "open_folder"),
    ("resimler aç", "open_folder"),
    ("müzikler aç", "open_folder"),
    ("videolar aç", "open_folder"),
    ("desktop aç", "open_folder"),
    ("downloads aç", "open_folder"),
    ("documents aç", "open_folder"),

    # unknown (10 örnek)
    ("", "unknown"),
    ("asdasd", "unknown"),
    ("bilinmeyen komut", "unknown"),
    ("123456", "unknown"),
    ("lorem ipsum", "unknown"),
    ("bilmiyorum", "unknown"),
    ("?", "unknown"),
    ("geç", "unknown"),
    ("qwerty", "unknown"),
    ("anlamsız metin", "unknown"),
]

# 2. Veri ayrıştırma
X_train = [x[0] for x in training_data]  # Komutlar
y_train = [x[1] for x in training_data]  # İntent'ler

# 3. NLP pipeline (TF-IDF + LogisticRegression)
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression())
])

# 4. Modeli eğit
model.fit(X_train, y_train)

# 5. Modeli kaydet
# Modeli (sadece classifier) ve vectorizer'ı ayrı ayrı kaydet
vectorizer = model.named_steps['tfidf']
classifier = model.named_steps['clf']

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

with open('intent_model.pkl', 'wb') as f:
    pickle.dump(classifier, f)

print("✅ Model ve vectorizer başarıyla intent_model.pkl ve vectorizer.pkl olarak kaydedildi.")

# Not: Kendi komutlarınızı ve varyasyonlarınızı buraya ekleyebilirsiniz.
# Örneğin: training_data.append(("benim yeni komutum", "get_time"))
