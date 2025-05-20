# launcher.py
import os
import subprocess
import platform
import re
import json
import shutil

APPS_FILE = "apps.json"

# Sistem klasörleri ve özel yollar
SYSTEM_PATHS = {
    "c": "C:\\",
    "d": "D:\\",
    "e": "E:\\",
    "f": "F:\\",
    "g": "G:\\",
    "h": "H:\\",
    "çöp": "shell:RecycleBinFolder",
    "çöp kutusu": "shell:RecycleBinFolder",
    "masaüstü": os.path.expandvars("%USERPROFILE%\\Desktop"),
    "indirilenler": os.path.expandvars("%USERPROFILE%\\Downloads"),
    "belgelerim": os.path.expandvars("%USERPROFILE%\\Documents"),
    "resimlerim": os.path.expandvars("%USERPROFILE%\\Pictures"),
    "müziklerim": os.path.expandvars("%USERPROFILE%\\Music"),
    "videolarım": os.path.expandvars("%USERPROFILE%\\Videos"),
    "gezgin": "explorer.exe",
    "dosya gezgini": "explorer.exe",
    "denetim masası": "control.exe",
    "ayarlar": "ms-settings:",
    "başlat": "shell:AppsFolder",
    "programlar": os.path.expandvars("%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs"),
    "kullanıcı programları": os.path.expandvars("%AppData%\\Microsoft\\Windows\\Start Menu\\Programs")
}

# Varsayılan uygulama yolları
DEFAULT_APPS = {
    "spotify": [
        "Spotify.exe",
        os.path.expandvars("%APPDATA%\\Spotify\\Spotify.exe"),
        "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe"
    ],
    "steam": [
        "Steam.exe",
        "C:\\Program Files (x86)\\Steam\\Steam.exe",
        "C:\\Program Files\\Steam\\Steam.exe",
        "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Steam\\Steam.lnk"
    ],
    "repo": [
        "C:\\Users\\İlayda\\Desktop\\R.E.P.O..url",
        "R.E.P.O..url"
    ],
    "chrome": "chrome.exe",
    "notepad": "notepad.exe",
    "word": [],
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe"
}

def load_app_mappings():
    """Kayıtlı uygulama yollarını yükle"""
    if os.path.exists(APPS_FILE):
        with open(APPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_APPS

def save_app_mappings(mappings):
    """Uygulama yollarını kaydet"""
    with open(APPS_FILE, "w", encoding="utf-8") as f:
        json.dump(mappings, f, ensure_ascii=False, indent=2)

def prompt_for_path(app_name):
    """Kullanıcıdan uygulama yolunu al"""
    print(f"\n❓ '{app_name}' için olası yollar:")
    if app_name in DEFAULT_APPS:
        paths = DEFAULT_APPS[app_name] if isinstance(DEFAULT_APPS[app_name], list) else [DEFAULT_APPS[app_name]]
        for i, path in enumerate(paths, 1):
            print(f"{i}. {path}")
    
    path = input(f"\n❓ Lütfen tam yürütülebilir dosya yolunu girin (veya numara seçin): ").strip()
    num = path.strip().replace('.', '')
    if num.isdigit() and app_name in DEFAULT_APPS:
        paths = DEFAULT_APPS[app_name] if isinstance(DEFAULT_APPS[app_name], list) else [DEFAULT_APPS[app_name]]
        if 1 <= int(num) <= len(paths):
            path = paths[int(num)-1]
    
    # Eğer .lnk dosyasıysa, varlık kontrolü yapmadan döndür
    if path.lower().endswith('.lnk'):
        return path
    elif os.path.exists(path):
        return path
    elif shutil.which(path):
        return shutil.which(path)
    print("⚠️ Geçersiz yol. Atlanıyor.")
    return None

def try_open_path(path):
    """Verilen yolu açmayı dene"""
    try:
        if platform.system().lower() == "windows":
            # Özel shell yolları için
            if path.startswith("shell:"):
                subprocess.Popen(['explorer.exe', path])
            # ms-settings için
            elif path.startswith("ms-settings:"):
                subprocess.Popen(['explorer.exe', path])
            # Kısayol dosyası ise hedefini bulup açmayı dene
            elif path.lower().endswith('.lnk'):
                try:
                    import pythoncom
                    from win32com.shell import shell, shellcon
                    shortcut = pythoncom.CoCreateInstance(
                        shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                    persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
                    persist_file.Load(path)
                    target_path, _ = shortcut.GetPath(shell.SLGP_UNCPRIORITY)
                    if target_path and os.path.exists(target_path):
                        if target_path.lower().endswith('.exe'):
                            os.startfile(target_path)
                            return True
                        else:
                            print(f"⚠️ Kısayolun hedefi bir .exe dosyası değil: {target_path}")
                            return False
                    else:
                        print(f"⚠️ Kısayolun hedefi bulunamadı veya erişilemiyor: {target_path}")
                        return False
                except ImportError:
                    print("⚠️ Kısayolun hedefini bulmak için pywin32 (pythoncom, win32com) modülleri gerekli. Lütfen 'pip install pywin32' komutunu çalıştırın.")
                    return False
                except Exception as e:
                    print(f"⚠️ Kısayol dosyası açılamadı: {e}\nKısayolun hedefi bozuk veya erişilemiyor olabilir.")
                    return False
            # Normal dosya/klasör için
            else:
                try:
                    os.startfile(path)
                except Exception as e:
                    print(f"⚠️ Dosya açılamadı: {e}")
                    return False
            return True
        elif platform.system().lower() == "darwin":
            subprocess.run(["open", "-a", path])
            return True
        else:
            subprocess.run([path], check=True)
            return True
    except Exception as e:
        print(f"⚠️ Hata: {e}")
        return False

def open_app(cmd: str) -> str:
    # 1) Uygulama adını regex ile çıkar
    m = re.search(r"([a-z0-9çğıöşü ]+?)(?:'ı|'i|ı|i)? aç", cmd)
    if not m:
        return "Lütfen şöyle deneyin: 'Spotify'ı aç' gibi."
    app_name = m.group(1).strip().lower()

    # 2) Önce sistem yollarında ara
    if app_name in SYSTEM_PATHS:
        path = SYSTEM_PATHS[app_name]
        if try_open_path(path):
            return ""  # Başarılı

    # 3) Sonra PATH üzerinde ara
    exe_path = shutil.which(app_name)
    
    # 4) Yoksa kayıtlı mapping'te ara
    mappings = load_app_mappings()
    if not exe_path and app_name in mappings:
        paths = mappings[app_name] if isinstance(mappings[app_name], list) else [mappings[app_name]]
        for path in paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path) and try_open_path(expanded_path):
                return ""  # Başarılı
            elif os.path.exists(path) and try_open_path(path):
                return ""  # Başarılı

    # 5) Hâlâ yoksa kullanıcıdan al ve kaydet
    if not exe_path:
        user_path = prompt_for_path(app_name)
        if user_path:
            mappings[app_name] = user_path
            save_app_mappings(mappings)
            if try_open_path(user_path):
                return ""  # Başarılı
        else:
            return f"Uygulama yolu alınamadı."

    # 6) Son çare olarak PATH'teki yolu dene
    if exe_path and try_open_path(exe_path):
        return ""  # Başarılı

    return f"Uygulama açılamadı: {app_name}"
