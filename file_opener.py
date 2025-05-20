import os
import subprocess
import platform

def open_file(file_name):
    # Kullanıcının masaüstü, belgeler, vs. gibi yaygın dizinleri kontrol et
    common_dirs = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.path.join(os.path.expanduser("~"), "Downloads")
    ]

    for directory in common_dirs:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            try:
                if platform.system() == "Windows":
                    os.startfile(file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.call(["open", file_path])
                else:  # Linux
                    subprocess.call(["xdg-open", file_path])
                return f"📂 {file_name} dosyası açılıyor."
            except Exception as e:
                return f"❌ Dosya açılırken hata oluştu: {str(e)}"
    
    return f"❌ {file_name} dosyası bulunamadı."
