import psutil
import shutil

def get_ram_info():
    mem = psutil.virtual_memory()
    total = round(mem.total / (1024**3), 2)
    used = round(mem.used / (1024**3), 2)
    percent = mem.percent
    return f"💾 RAM: {used} GB / {total} GB (%{percent} kullanılıyor)"

def get_disk_info():
    total, used, free = shutil.disk_usage("/")
    total_gb = round(total / (1024**3), 2)
    free_gb = round(free / (1024**3), 2)
    return f"📂 Disk: Toplam {total_gb} GB, Boş {free_gb} GB"

def get_cpu_info():
    usage = psutil.cpu_percent(interval=1)
    return f"🧠 İşlemci Kullanımı: %{usage}"

def get_all_status():
    return "\n".join([
        get_ram_info(),
        get_disk_info(),
        get_cpu_info()
    ])
