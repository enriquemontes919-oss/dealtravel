"""
agents/liverpool.py — Agente Liverpool MX
Catálogo curado con productos reales de sus secciones de oferta.
URLs directas a categorías de sale en liverpool.com.mx
"""
from agents.base import precio_original, ahora_str

LIVERPOOL_PRODUCTOS = [
    # Electrónica
    ("Liverpool — Smart TV Samsung 55\" 4K QLED",   12999, 30, "electronico",
     "https://www.liverpool.com.mx/tienda/brand/samsung?facetFilters=brand_description%3ASAMSUNG&pageType=plp"),
    ("Liverpool — iPhone 15 128GB",                 16999, 15, "electronico",
     "https://www.liverpool.com.mx/tienda/brand/apple?facetFilters=brand_description%3AAPPLE"),
    ("Liverpool — Laptop HP 15\" Core i5 8GB RAM",   9999, 20, "electronico",
     "https://www.liverpool.com.mx/tienda/cat/laptops?facetFilters="),
    ("Liverpool — Audífonos Sony WH-1000XM5",        5999, 25, "electronico",
     "https://www.liverpool.com.mx/tienda/brand/sony"),
    ("Liverpool — iPad 10ma Gen 64GB WiFi",          8499, 15, "electronico",
     "https://www.liverpool.com.mx/tienda/brand/apple"),
    # Moda
    ("Liverpool — Tenis Nike Air Max 270 Hombre",    2199, 20, "moda",
     "https://www.liverpool.com.mx/tienda/brand/nike?facetFilters=brand_description%3ANIKE"),
    ("Liverpool — Tenis Adidas Ultraboost 22",       2799, 25, "moda",
     "https://www.liverpool.com.mx/tienda/brand/adidas?facetFilters=brand_description%3AADIDAS"),
    ("Liverpool — Chamarra Tommy Hilfiger Hombre",   2499, 30, "moda",
     "https://www.liverpool.com.mx/tienda/brand/tommy-hilfiger"),
    ("Liverpool — Bolsa Coach Dreamer Piel",         4999, 35, "moda",
     "https://www.liverpool.com.mx/tienda/brand/coach"),
    ("Liverpool — Perfume CH Good Girl 80ml",        1899, 20, "belleza",
     "https://www.liverpool.com.mx/tienda/cat/perfumes-para-dama"),
    # Hogar
    ("Liverpool — Cafetera Nespresso Vertuo Pop",    1999, 25, "hogar",
     "https://www.liverpool.com.mx/tienda/brand/nespresso"),
    ("Liverpool — Aspiradora Robot iRobot Roomba",   5999, 30, "hogar",
     "https://www.liverpool.com.mx/tienda/cat/aspiradoras-robot"),
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
