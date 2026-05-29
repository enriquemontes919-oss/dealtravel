"""
agents/amazon.py — Agente Amazon MX
Mayo 2026: URLs cambiadas a búsquedas por categoría + tag de afiliado.
Los ASINs individuales causan 404 cuando el producto se descataloga.
Búsquedas garantizan landing válido siempre.
"""
from agents.base import AMAZON_TAG, precio_original, ahora_str

def amazon_search_url(query):
    """URL de búsqueda Amazon MX con tag de afiliado — siempre válida"""
    import urllib.parse
    q = urllib.parse.quote_plus(query)
    return f"https://www.amazon.com.mx/s?k={q}&tag={AMAZON_TAG}"

PRODUCTOS = [
    # (nombre, precio, descuento, tipo, query_busqueda)
    ("iPhone 15 128GB Negro",                  17999, 10, "electronico", "iphone 15 128gb"),
    ("Samsung Galaxy S24 256GB",               15999, 12, "electronico", "samsung galaxy s24 256gb"),
    ("iPad 10ma generación 64GB WiFi",          8499, 10, "electronico", "ipad 10 generacion 64gb"),
    ("Sony WH-1000XM5 Audífonos Bluetooth",     5599, 20, "electronico", "sony wh-1000xm5 audifonos"),
    ("Nintendo Switch OLED Blanco",             7199, 10, "electronico", "nintendo switch oled"),
    ("Samsung Smart TV 55\" 4K Crystal UHD",   10999, 20, "electronico", "samsung smart tv 55 4k"),
    ("Laptop HP 15 Core i5 8GB 512GB SSD",      9499, 15, "electronico", "laptop hp 15 core i5"),
    ("Apple Watch SE 2da Gen 44mm",             5999, 15, "electronico", "apple watch se 2 44mm"),
    ("Echo Dot 5ta Generación Alexa",            899, 30, "electronico", "echo dot 5ta generacion"),
    ("Fire TV Stick 4K Max",                   1299, 25, "electronico", "fire tv stick 4k max"),
    ("Cafetera Nespresso Vertuo Pop",           1999, 20, "hogar",       "cafetera nespresso vertuo"),
    ("Instant Pot Duo 7 en 1 6QT",             1499, 25, "hogar",       "instant pot duo 6qt"),
    ("Roomba 694 Aspiradora Robot",             4499, 20, "hogar",       "roomba aspiradora robot"),
    ("Perfume Carolina Herrera Good Girl 80ml", 1799, 15, "belleza",     "carolina herrera good girl 80ml"),
    ("CeraVe Crema Hidratante 340g",             399, 20, "belleza",     "cerave crema hidratante"),
    ("Tenis Nike Air Max 270 Hombre",           2199, 25, "moda",        "nike air max 270 hombre"),
    ("Mochila Samsonite Guardit 2.0 20L",        899, 20, "moda",        "mochila samsonite guardit"),
    ("Control Xbox Series Inalámbrico",          899, 15, "electronico", "control xbox series inalambrico"),
]

def run():
    ofertas = []
    for nombre, precio, descuento, tipo, query in PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Amazon MX",
            "tipo":            tipo,
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             amazon_search_url(query),
            "tipo_promo":      f"-{descuento}% Oferta Amazon",
            "palabras_clave":  nombre.lower(),
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Amazon MX] {len(ofertas)} ofertas")
    return ofertas
