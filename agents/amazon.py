"""
agents/amazon.py — Agente Amazon MX (catálogo hardcodeado con ASINs reales)
Fase 2: reemplazar con Scraperapi para precios en tiempo real
"""
from agents.base import amazon_url, precio_original, ahora_str

PRODUCTOS = [
    ("Apple iPhone 15 128GB",              0,    0,   "electronico", "B0CHX8VZ2N"),
    ("Samsung Galaxy S24 256GB",           0,    0,   "electronico", "B0CQ7R738Y"),
    ("MacBook Air M2 256GB",               0,    0,   "electronico", "B0B3C1N9FY"),
    ("iPad 10ma generación 64GB",          0,    0,   "electronico", "B0BJLF2BRM"),
    ("Sony WH-1000XM5 Audífonos",          0,    0,   "electronico", "B09XS7JWHH"),
    ("Nintendo Switch OLED",               0,    0,   "electronico", "B098RKWHHZ"),
    ("Samsung Smart TV 55\" 4K",           0,    0,   "electronico", "B0BN7FYKQM"),
    ("Laptop HP 15 Core i5 8GB",           0,    0,   "electronico", "B0BX5CPGX5"),
    ("PlayStation 5 Slim",                 0,    0,   "electronico", "B0CL61F39H"),
    ("Apple Watch Series 9",               0,    0,   "electronico", "B0CHX8H5LQ"),
    ("Cafetera Nespresso Vertuo",          0,    0,   "hogar",       "B07THHQMHM"),
    ("Instant Pot Duo 7 en 1",             0,    0,   "hogar",       "B00FLYWNYQ"),
    ("Roomba i3 Aspiradora Robot",         0,    0,   "hogar",       "B08H6NJBJ7"),
    ("Báscula Digital Xiaomi",             0,    0,   "hogar",       "B07H243WM8"),
    ("Perfume Carolina Herrera Good Girl", 0,    0,   "belleza",     "B01N1WJUQ6"),
    ("Crema Facial CeraVe Hidratante",     0,    0,   "belleza",     "B000YJ2SKS"),
    ("Tenis Nike Air Max 270 Hombre",   2199,   25,   "moda",        "B07D26TJ58"),
    ("Mochila Samsonite 20L",            899,   20,   "moda",        "B082NKS553"),
]

def run():
    ofertas = []
    for nombre, precio, descuento, tipo, asin in PRODUCTOS:
        sin_precio = precio == 0
        orig = precio_original(precio, descuento) if not sin_precio and descuento > 0 else None
        ofertas.append({
            "fuente":          "Amazon MX",
            "tipo":            tipo,
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      "Ver precio" if sin_precio else f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento if not sin_precio else None,
            "url":             amazon_url(asin),
            "tipo_promo":      "Oferta Amazon" if sin_precio else f"-{descuento}% Oferta Amazon",
            "palabras_clave":  nombre.lower(),
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Amazon MX] {len(ofertas)} ofertas")
    return ofertas

