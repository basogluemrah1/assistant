# main.py

from clock import get_time
import re
from math_ops import calculate
from weather import get_weather
from launcher import open_app, DEFAULT_APPS, try_open_path
import gradio as gr
from search import web_search
from news import get_news
from youtube_player import search_youtube_videos, open_video_by_index, search_and_open_video
from logger import log_command, get_command_history, clear_command_history, get_frequent_commands
from file_manager import open_folder
from system_status import get_all_status
from file_opener import open_file
import os
import shutil
from intent_classifier import predict_intent


# Konsol için durum değişkenleri
waiting_for_app_path = False
last_app_name = ""


def process_command(cmd):
    global waiting_for_app_path, last_app_name
    cmd = cmd.strip().lower()
    
    # Uygulama yolu için bekleme durumundaysak
    if waiting_for_app_path and last_app_name:
        waiting_for_app_path = False
        app_name = last_app_name
        last_app_name = ""
        
        # Eğer numara girdiyse
        if cmd.isdigit() and app_name in DEFAULT_APPS:
            paths = DEFAULT_APPS[app_name] if isinstance(DEFAULT_APPS[app_name], list) else [DEFAULT_APPS[app_name]]
            if 1 <= int(cmd) <= len(paths):
                path = paths[int(cmd)-1]
                if try_open_path(path):
                    return "✅ Uygulama açıldı."
                else:
                    return f"❌ Uygulama açılamadı: {path}"
        
        # Direkt yol girdiyse
        if os.path.exists(cmd) or shutil.which(cmd) or cmd.lower().endswith('.lnk'):
            if try_open_path(cmd):
                return "✅ Uygulama açıldı."
            else:
                return f"❌ Uygulama açılamadı: {cmd}"
        
        return "⚠️ Geçersiz yol. Lütfen tekrar deneyin."
    
    # Komut geçmişini silme (manuel kontrol edilen ilk özel durum)
    if "geçmişi sil" in cmd or "komut geçmişini sil" in cmd or "geçmişi temizle" in cmd or "komut geçmişini temizle" in cmd:
        return clear_command_history()

    # ⬇️ Yeni kısım: intent tahmini
    intent = predict_intent(cmd)
    print(f"[INTENT] Tahmin edilen intent: {intent}")  # Debug için
    
    # Komutu geçmişe kaydet
    log_command(cmd)

    # YouTube arama sonrası kısa seçim komutları (intent ile birlikte)
    if getattr(process_command, "last_youtube_search", False):
        if re.fullmatch(r"\d+(\s*\.)?", cmd.strip()):
            process_command.last_youtube_search = False
            return open_video_by_index(cmd)

    # Intent tabanlı komutlar
    if intent == "exit":
        return "Görüşürüz! 👋"
    elif intent == "show_history":
        return get_command_history()
    elif intent == "get_weather":
        weather_info = get_weather(cmd)
        return f"🌤️ {weather_info}"
    elif intent == "get_news":
        return get_news()
    elif intent == "search_youtube":
        # YouTube izleme komutu için kontrol (örn: "youtube gandhi filmini izle")
        watch_patterns = ["izle", "seyret", "oynat", "aç video", "aç"]
        
        # Sadece "aç" kontrolü için özel durum
        if cmd.strip().lower() == "youtube aç" or cmd.strip().lower() == "youtube'u aç":
            process_command.last_youtube_search = True
            return search_youtube_videos(cmd)
        elif any(pattern in cmd for pattern in watch_patterns):
            # Sorguyu temizle
            query = re.sub(r"(youtube'da|youtube|youtub|yutub|yutup)", "", cmd, flags=re.IGNORECASE).strip()
            query = re.sub(r"(izle|seyret|oynat|aç video|aç)", "", query, flags=re.IGNORECASE).strip()
            
            # Eğer temizlenmiş sorgu varsa, videoyu ara ve aç
            if query.strip():
                return search_and_open_video(query)
            else:
                # Sadece "youtube aç" veya benzer komut varsa ana sayfayı aç
                process_command.last_youtube_search = True
                return search_youtube_videos(cmd)
        else:
            # Normal YouTube aramaya devam et
            process_command.last_youtube_search = True
            return search_youtube_videos(cmd)
    elif intent == "open_youtube_video":
        process_command.last_youtube_search = False
        result = open_video_by_index(cmd)
        return result if result else "Geçerli bir seçim yapamadım."
    elif intent == "get_system_status":
        return get_all_status()
    elif intent == "get_time":
        current = get_time()
        return f"⌚ Şu an saat: {current}"
    elif intent == "web_search":
        return web_search(cmd)
    elif intent == "open_folder":
        for keyword in ["masaüstü", "indirilenler", "belgeler", "resimler", "müzikler", "videolar"]:
            if keyword in cmd:
                return open_folder(keyword)
        return "Hangi klasörü açmak istediğini anlayamadım."
    elif intent == "open_file":
        match = re.search(r"(.+?)\.([a-z0-9]+)", cmd)
        if match:
            file_name = match.group(0)
            return open_file(file_name)
        elif "dosya" in cmd:
            return "📄 Hangi dosyayı açmak istediğini anlayamadım. Lütfen tam dosya adını ve uzantısını yaz (ör: belge.pdf)"
        match2 = re.search(r"([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)\s+aç", cmd)
        if match2:
            file_name = f"{match2.group(1)}.{match2.group(2)}"
            return open_file(file_name)
        else:
            app_name = cmd.replace("aç", "").strip()
            if app_name:
                waiting_for_app_path = True
                last_app_name = app_name
                return prompt_for_path(app_name)
            return "❌ Hangi uygulamayı açmak istediğini anlayamadım."
    elif intent == "open_app":
        app_name = cmd.replace("aç", "").strip()
        if app_name:
            # Önce direkt open_app ile açmayı dene
            result = open_app(f"{app_name} aç")
            # Eğer boş string dönerse başarılı demektir
            if result == "":
                return "✅ Uygulama açıldı."
            # Eğer "Uygulama açılamadı" dönerse, yol sormak gerekiyor
            elif "Uygulama açılamadı" in result or "yolu alınamadı" in result:
                waiting_for_app_path = True
                last_app_name = app_name
                return prompt_for_path(app_name)
            # Diğer durumlarda hatayı göster
            else:
                return result
        return "❌ Hangi uygulamayı açmak istediğini anlayamadım."
    elif intent == "calculate":
        result = calculate(cmd)
        return f"Sonuç: {result}"
    else:
        return "Bu komutu henüz tanımıyorum. 🤔"

def run_console():
    print("🚀 Asistan başlatıldı. Çıkmak için 'çıkış' yazın.\n")
    while True:
        cmd = input("Komutun: ").strip().lower()
        response = process_command(cmd)
        print(response)
        if "Görüşürüz" in response:
            break

def run_web():
    with gr.Blocks(title="🧠 Akıllı Asistan") as demo:
        gr.Markdown("## 🤖 Hoş geldin! Komut yaz veya önerilere tıkla.")

        chatbot = gr.Chatbot(label="Asistan ile Sohbet", height=400)
        msg = gr.Textbox(
            placeholder="Bir komut yazın...",
            label="Komut",
            show_label=True
        )
        clear_btn = gr.Button("🧹 Sohbeti Temizle")
        state = gr.State([("🤖", "Merhaba! Size nasıl yardımcı olabilirim?")])
        path_state = gr.State("")  # Uygulama yolu için state

        gr.Markdown("### 🧠 En Sık Kullandığın Komutlar:")

        # Sık komutlar için dinamik buton alanı
        dynamic_buttons = []

        def get_dynamic_suggestions():
            frequent_cmds = get_frequent_commands()
            return frequent_cmds

        def cevapla(history, user_input, path_input):
            history = history + [("Sen", user_input)]
            
            # Eğer path_input varsa ve son mesaj yol sorma mesajıysa
            if path_input and history[-2][1].startswith("❓"):
                app_name = history[-2][1].split("'")[1]  # Uygulama adını al
                if path_input.isdigit() and app_name in DEFAULT_APPS:
                    paths = DEFAULT_APPS[app_name] if isinstance(DEFAULT_APPS[app_name], list) else [DEFAULT_APPS[app_name]]
                    if 1 <= int(path_input) <= len(paths):
                        path_input = paths[int(path_input)-1]
                
                if path_input.lower().endswith('.lnk') or os.path.exists(path_input) or shutil.which(path_input):
                    try:
                        os.startfile(path_input)
                        response = "✅ Uygulama açıldı."
                    except Exception as e:
                        response = f"❌ Uygulama açılamadı: {str(e)}"
                else:
                    response = "⚠️ Geçersiz yol. Lütfen tekrar deneyin."
            else:
                response = process_command(user_input)
            
            history = history + [("🤖", response)]
            return history, "", ""  # Boş path_input döndür

        # Textbox'tan gönder
        msg.submit(cevapla, [state, msg, path_state], [chatbot, msg, path_state])

        # Temizleme
        clear_btn.click(lambda: ([("🤖", "Merhaba! Size nasıl yardımcı olabilirim?")], "", ""), outputs=[chatbot, msg, path_state])

        # Dinamik butonlar
        def create_buttons():
            cmds = get_dynamic_suggestions()
            buttons = []
            for cmd_text in cmds:
                btn = gr.Button(cmd_text)
                btn.click(fn=cevapla, inputs=[state, gr.State(cmd_text), path_state], outputs=[chatbot, msg, path_state])
                buttons.append(btn)
            return buttons

        with gr.Row():
            dynamic_buttons = create_buttons()

        # Sabit önerilen komutlar
        with gr.Row():
            gr.Markdown("### 🔖 Önerilen Komutlar:")
        with gr.Row():
            btn_weather = gr.Button("🌤️ Hava Durumu")
            btn_time = gr.Button("🕒 Saat Kaç?")
            btn_news = gr.Button("📰 Haberler")
            btn_youtube = gr.Button("▶️ YouTube'da Gülme Videoları")
            btn_ram = gr.Button("💾 RAM Durumu")

        btn_weather.click(fn=cevapla, inputs=[state, gr.State("hava durumu nasıl?"), path_state], outputs=[chatbot, msg, path_state])
        btn_time.click(fn=cevapla, inputs=[state, gr.State("saat kaç"), path_state], outputs=[chatbot, msg, path_state])
        btn_news.click(fn=cevapla, inputs=[state, gr.State("haberler neler"), path_state], outputs=[chatbot, msg, path_state])
        btn_youtube.click(fn=cevapla, inputs=[state, gr.State("youtube'da gülme videoları"), path_state], outputs=[chatbot, msg, path_state])
        btn_ram.click(fn=cevapla, inputs=[state, gr.State("ram durumu"), path_state], outputs=[chatbot, msg, path_state])

    demo.launch()

def prompt_for_path(app_name):
    """Kullanıcıdan uygulama yolunu al"""
    message = f"\n❓ '{app_name}' için olası yollar:\n"
    if app_name in DEFAULT_APPS:
        paths = DEFAULT_APPS[app_name] if isinstance(DEFAULT_APPS[app_name], list) else [DEFAULT_APPS[app_name]]
        for i, path in enumerate(paths, 1):
            message += f"{i}. {path}\n"
    
    message += f"\n❓ Lütfen tam yürütülebilir dosya yolunu girin (veya numara seçin): "
    return message

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        run_web()
    else:
        run_console()
