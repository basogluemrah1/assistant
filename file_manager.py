import os
import platform
import subprocess

def open_folder(folder_name):
    paths = {
        "masaüstü": os.path.join(os.path.expanduser("~"), "Desktop"),
        "indirilenler": os.path.join(os.path.expanduser("~"), "Downloads"),
        "belgeler": os.path.join(os.path.expanduser("~"), "Documents"),
        "resimler": os.path.join(os.path.expanduser("~"), "Pictures"),
        "müzikler": os.path.join(os.path.expanduser("~"), "Music"),
        "videolar": os.path.join(os.path.expanduser("~"), "Videos"),
    }
    path = paths.get(folder_name)
    if path and os.path.exists(path):
        os.startfile(path)
        return f"{folder_name.capitalize()} klasörü açıldı."
    else:
        return f"{folder_name.capitalize()} klasörü bulunamadı."
