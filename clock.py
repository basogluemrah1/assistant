from datetime import datetime

def get_time():
    """Mevcut saati döndürür"""
    return datetime.now().strftime("%H:%M:%S")

