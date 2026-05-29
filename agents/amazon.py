"""
agents/amazon.py — Agente Amazon MX (catálogo hardcodeado con ASINs reales)

REVISIÓN Mayo 2026:
- Todos los productos ahora tienen precio real en MXN (sin "Ver precio")
- ASINs verificados como activos en amazon.com.mx
- Eliminados ASINs que daban 404 o redirigían a error
- Fase 2: reemplazar con Scraperapi/PA API para precios en tiempo real
"""
from agents.base import amazon_url, precio_original, ahora_str

# Formato: (nombre, precio_mxn, descuento_pct, tipo, asin)
# Precios de referencia reales al momento de curación — Mayo 2026
PRODUCTOS = [
    # Electrónica
    ("iPhone 15 128GB Negro",                  17999, 10, "electronico", "B0CHX8VZ2N"),
    ("Samsung Galaxy S24 256GB",               15999, 12, "electronico", "B0CQ7R738Y"),
    ("iPad 10ma generación 64GB WiFi",          8499, 10, "electronico", "B0BJLF2BRM"),
    ("Sony WH-1000XM5 Audífonos Bluetooth",     5599, 20, "electronico", "B09XS7JWHH"),
    ("Nintendo Switch OLED Blanco",             7199, 10, "electronico", "B098RKWHHZ"),
    ("Samsung Smart TV 55\" 4K Crystal UHD",   10999, 20, "electronico", "B0BN7FYKQM"),
    ("Laptop HP 15 Core i5 8GB 512GB SSD",      9499, 15, "electronico", "B0BX5CPGX5"),
    ("Apple Watch SE 2da Gen 44mm",             5999, 15, "electronico", "B0CHX8H5LQ"),
    ("Echo Dot 5ta Generación Alexa",            899, 30, "electronico", "B09B8RVKGX"),
    ("Fire TV Stick 4K Max",                   1299, 25, "electronico", "B0B484HVN7"),
    # Hogar
    ("Cafetera Nespresso Vertuo Pop",           1999, 20, "hogar",       "B09SZNPJH9"),
    ("Instant Pot Duo 7 en 1 6QT",             1499, 25, "hogar",       "B00FLYWNYQ"),
    ("Roomba 694 Aspiradora Robot",             4499, 20, "hogar",       "B08H6NJBJ7"),
    # Belleza
    ("Perfume Carolina Herrera Good Girl 80ml", 1799, 15, "belleza",     "B01N1WJUQ6"),
    ("CeraVe Crema Hidratante 340g",             399, 20, "belleza",     "B000YJ2SKS"),
    # Moda
    ("Tenis Nike Air Max 270 Hombre",           2199, 25, "moda",        "B07D26TJ58"),
    ("Mochila Samsonite Guardit 2.0 20L",        899, 20, "moda",        "B082NKS553"),
    # Gaming
    ("Control Xbox Series Inalámbrico",          899, 15, "electronico", "B08DF248LD"),
]

def run():
    ofertas = []
    for nombre, precio, descuento, tipo, asin in PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Amazon MX",
            "tipo":            tipo,
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             amazon_url(asin),
            "tipo_promo":      f"-{descuento}% Oferta Amazon",
            "palabras_clave":  nombre.lower(),
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Amazon MX] {len(ofertas)} ofertas")
    return ofertas
