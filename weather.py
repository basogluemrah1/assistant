# weather.py
import requests
import re

WEATHER_CODES = {
    0: "açık gökyüzü", 1: "az bulutlu", 2: "parçalı bulutlu", 3: "bulutlu",
    45: "sisli", 48: "yağmur çisi", 51: "hafif çiseleme", 53: "orta çiseleme",
    55: "yoğun çiseleme", 61: "hafif yağmur", 63: "orta yağmur", 65: "yoğun yağmur",
    71: "hafif kar", 73: "orta kar", 75: "yoğun kar", 80: "hafif sağanak",
    81: "orta sağanak", 82: "yoğun sağanak"
}

def get_weather(cmd: str) -> str:
    # 1) Şehir adı ayrıştırması: "istanbul'da hava" veya "izmir de sıcaklık"
    m = re.search(r"([a-zçğıöşü]+)(?:'da|'de| da| de)\s+(hava|sıcaklık)", cmd)
    if not m:
        return "Lütfen şöyle deneyin: 'İstanbul'da hava nasıl?' veya 'Ankara da sıcaklık?'"
    city = m.group(1)
    
    # 2) Geocoding API çağrısı
    geo_url = (
        f"https://geocoding-api.open-meteo.com/v1/search"
        f"?name={city}&count=1&language=tr&format=json"
    )
    try:
        geo_resp = requests.get(geo_url, timeout=5)
        geo_data = geo_resp.json()
        results = geo_data.get("results")
        if not results:
            return f"Şehir bulunamadı: {city}"
        loc = results[0]
        lat, lon = loc["latitude"], loc["longitude"]
    except Exception as e:
        return f"Coğrafi konum hatası: {e}"
    
    # 3) Hava durumu API çağrısı
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&timezone=Europe%2FIstanbul"
    )
    try:
        w_resp = requests.get(weather_url, timeout=5)
        w_data = w_resp.json()
        cw = w_data.get("current_weather")
        if not cw:
            return "Hava verisi alınamadı."
        temp = cw["temperature"]
        code = cw["weathercode"]
        desc = WEATHER_CODES.get(code, f"(kod {code})")
        return f"{city.title()} için hava: {desc}, sıcaklık: {temp:.1f}°C"
    except Exception as e:
        return f"Hava durumunda hata: {e}"
