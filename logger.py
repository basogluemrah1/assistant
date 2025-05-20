# logger.py

from datetime import datetime
from collections import Counter

COMMAND_LOG = "commands.log"

def log_command(cmd: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(COMMAND_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {cmd}\n")

def get_command_history(limit=20):
    try:
        with open(COMMAND_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return "".join(lines[-limit:]) if lines else "Hiç komut geçmişi bulunamadı."
    except FileNotFoundError:
        return "Henüz hiç komut geçmişi oluşturulmamış."

def clear_command_history():
    try:
        with open(COMMAND_LOG, "w", encoding="utf-8") as f:
            f.write("")  # Dosyayı temizle
        return "Komut geçmişi temizlendi. 🧹"
    except Exception as e:
        return f"Geçmiş silinirken bir hata oluştu: {e}"

def get_frequent_commands(n=5):
    try:
        with open(COMMAND_LOG, "r", encoding="utf-8") as file:
            commands = [line.strip().lower() for line in file if line.strip()]
        most_common = Counter(commands).most_common(n)
        return [cmd for cmd, _ in most_common]
    except Exception as e:
        return []
