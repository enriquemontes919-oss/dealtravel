"""
agents/amazon.py — Agente Amazon MX
URLs de búsqueda con tag de afiliado — sin mostrar precio.
El usuario llega a resultados reales de Amazon con el producto buscado.
"""
from agents.base import AMAZON_TAG, ahora_str
from urllib.parse import quote_plus

def amazon_search_url(query):
    return f"https://www.amazon.com.mx/s?k={quote_plus(query)}&tag={AMAZON_TAG}"

PRODUCTOS = [
    ("iPhone 15 128GB",                    "electronico", "iphone 15 128gb"),
    ("Samsung Galaxy S24 256GB",           "electronico", "samsung galaxy s24"),
    ("iPad 10ma generación 64GB WiFi",     "electronico", "ipad 10 generacion"),
    ("Sony WH-1000XM5 Audífonos",          "electronico", "sony wh-1000xm5"),
    ("Nintendo Switch OLED",               "electronico", "nintendo switch oled"),
    ("Samsung Smart TV 55\" 4K",           "electronico", "samsung smart tv 55 4k"),
    ("Laptop HP 15 Core i5 8GB",           "electronico", "laptop hp 15 core i5"),
    ("Apple Watch SE 2da Gen",             "electronico", "apple watch se 2"),
    ("Echo Dot 5ta Generación Alexa",      "electronico", "echo dot 5ta generacion"),
    ("Fire TV Stick 4K Max",               "electronico", "fire tv stick 4k"),
    ("Cafetera Nespresso Vertuo Pop",      "hogar",       "cafetera nespresso vertuo"),
    ("Instant Pot Duo 7 en 1",             "hogar",       "instant pot duo"),
    ("Roomba Aspiradora Robot",            "hogar",       "roomba aspiradora robot"),
    ("Perfume Carolina Herrera Good Girl", "belleza",     "carolina herrera good girl"),
    ("CeraVe Crema Hidratante",            "belleza",     "cerave crema hidratante"),
    ("Tenis Nike Air Max 270",             "moda",        "nike air max 270"),
    ("Mochila Samsonite Guardit",          "moda",        "mochila samsonite"),
    ("Control Xbox Series Inalámbrico",    "electronico", "control xbox series"),
]

def run():
    ofertas = []
    for nombre, tipo, query in PRODUCTOS:
        ofertas.append({
            "fuente":          "Amazon MX",
            "tipo":            tipo,
            "destino":         nombre,
            "precio":          0,
            "precio_fmt":      "Ver en Amazon →",
            "precio_original": None,
            "descuento_pct":   None,
            "url":             amazon_search_url(query),
            "tipo_promo":      "Ofertas Amazon MX",
            "palabras_clave":  nombre.lower(),
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Amazon MX] {len(ofertas)} productos")
    return ofertas
