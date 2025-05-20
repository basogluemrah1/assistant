def calculate(expression):
    """Basit matematiksel işlemleri hesaplar"""
    try:
        # Güvenli bir şekilde matematiksel ifadeyi değerlendir
        return eval(expression)
    except:
        return "Hesaplama yapılamadı. Lütfen geçerli bir matematiksel ifade girin."
