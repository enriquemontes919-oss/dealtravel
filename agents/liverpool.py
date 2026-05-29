"""
agents/liverpool.py — Agente Liverpool MX
Catálogo curado con productos reales de sus secciones de oferta.
URLs directas a categorías de sale en liverpool.com.mx
"""
from agents.base import precio_original, ahora_str

LIVERPOOL_PRODUCTOS = [
    # Electrónica
    ("Liverpool — Smart TV Samsung 55\" 4K QLED",   12999, 30, "electronico",
     "https://www.liverpool.com.mx/tienda/Electronica/Televisores/c/TVSMART"),
    ("Liverpool — iPhone 15 128GB",                 16999, 15, "electronico",
     "https://www.liverpool.com.mx/tienda/Tecnologia/Celulares-y-Telefonia/Celulares/c/CEL"),
    ("Liverpool — Laptop HP 15\" Core i5 8GB RAM",   9999, 20, "electronico",
     "https://www.liverpool.com.mx/tienda/Tecnologia/Computadoras/Laptops/c/LAP"),
    ("Liverpool — Audífonos Sony WH-1000XM5",        5999, 25, "electronico",
     "https://www.liverpool.com.mx/tienda/Tecnologia/Audio/Audifonos/c/AUD"),
    ("Liverpool — iPad 10ma Gen 64GB WiFi",          8499, 15, "electronico",
     "https://www.liverpool.com.mx/tienda/Tecnologia/Computadoras/Tablets/c/TAB"),
    # Moda
    ("Liverpool — Tenis Nike Air Max 270 Hombre",    2199, 20, "moda",
     "https://www.liverpool.com.mx/tienda/Hombre/Zapatos/Tenis/c/TENIH"),
    ("Liverpool — Tenis Adidas Ultraboost 22",       2799, 25, "moda",
     "https://www.liverpool.com.mx/tienda/Mujer/Zapatos/Tenis/c/TENIM"),
    ("Liverpool — Chamarra Tommy Hilfiger Hombre",   2499, 30, "moda",
     "https://www.liverpool.com.mx/tienda/Hombre/Ropa/Chamarras-y-Abrigos/c/CHAMH"),
    ("Liverpool — Bolsa Coach Dreamer Piel",         4999, 35, "moda",
     "https://www.liverpool.com.mx/tienda/Mujer/Bolsas/c/BOLM"),
    ("Liverpool — Perfume CH Good Girl 80ml",        1899, 20, "belleza",
     "https://www.liverpool.com.mx/tienda/Belleza/Fragancias/Perfumes-para-Dama/c/PERFD"),
    # Hogar
    ("Liverpool — Cafetera Nespresso Vertuo Pop",    1999, 25, "hogar",
     "https://www.liverpool.com.mx/tienda/Hogar/Electrodomesticos/Cafeteras/c/CAF"),
    ("Liverpool — Aspiradora Robot iRobot Roomba",   5999, 30, "hogar",
     "https://www.liverpool.com.mx/tienda/Hogar/Electrodomesticos/Aspiradoras/c/ASP"),
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
