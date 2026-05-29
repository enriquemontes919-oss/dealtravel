"""
agents/liverpool.py — Agente Liverpool MX
URLs verificadas desde Google Search — Mayo 2026
Estructura: liverpool.com.mx/tienda/categoria/catID
"""
from agents.base import precio_original, ahora_str

LIVERPOOL_PRODUCTOS = [
    # Electrónica
    ("Liverpool — Smart TV Samsung 55\" 4K QLED",   12999, 30, "electronico",
     "https://www.liverpool.com.mx/tienda/pantallas-y-televisores/catst77704435"),
    ("Liverpool — iPhone 15 128GB",                 16999, 15, "electronico",
     "https://www.liverpool.com.mx/tienda/celulares/cat5150024"),
    ("Liverpool — Laptop HP 15\" Core i5 8GB RAM",   9999, 20, "electronico",
     "https://www.liverpool.com.mx/tienda/computadoras-laptop/cat980042"),
    ("Liverpool — Audífonos Sony WH-1000XM5",        5999, 25, "electronico",
     "https://www.liverpool.com.mx/tienda/audifonos/catst16778857"),
    ("Liverpool — iPad 10ma Gen 64GB WiFi",          8499, 15, "electronico",
     "https://www.liverpool.com.mx/tienda/tablets/cat1010044"),
    # Moda
    ("Liverpool — Tenis Nike Air Max 270 Hombre",    2199, 20, "moda",
     "https://www.liverpool.com.mx/tienda/tenis-de-hombre/catst7543627"),
    ("Liverpool — Tenis Adidas Ultraboost 22",       2799, 25, "moda",
     "https://www.liverpool.com.mx/tienda/tenis/catst4760950"),
    ("Liverpool — Chamarra Tommy Hilfiger Hombre",   2499, 30, "moda",
     "https://www.liverpool.com.mx/tienda/chamarras-y-chalecos/catst55391142"),
    ("Liverpool — Bolsa Coach Dreamer Piel",         4999, 35, "moda",
     "https://www.liverpool.com.mx/tienda/bolsos-y-carteras/cat1100145"),
    ("Liverpool — Perfume CH Good Girl 80ml",        1899, 20, "belleza",
     "https://www.liverpool.com.mx/tienda/perfumes-para-dama/cat1100067"),
    # Hogar
    ("Liverpool — Cafetera Nespresso Vertuo Pop",    1999, 25, "hogar",
     "https://www.liverpool.com.mx/tienda/nespresso/catst81012509"),
    ("Liverpool — Aspiradora Robot iRobot Roomba",   5999, 30, "hogar",
     "https://www.liverpool.com.mx/tienda/aspiradoras/cat1000441"),
]

def run():
    ofertas = []
    for nombre, precio, descuento, tipo, url in LIVERPOOL_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Liverpool",
            "tipo":            tipo,
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             url,
            "tipo_promo":      f"-{descuento}% Oferta Liverpool",
            "palabras_clave":  nombre.lower(),
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Liverpool] {len(ofertas)} ofertas")
    return ofertas
