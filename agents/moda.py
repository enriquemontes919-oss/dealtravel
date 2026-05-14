"""
agents/moda.py — Agentes de tiendas de moda: Nike, Adidas, Puma, Zara, H&M
Catálogo curado con precios y descuentos reales.
Cuando Awin apruebe Nike/Adidas → reemplazar URLs por deep links de Product Feed.
"""
from agents.base import precio_original, ahora_str

# ── Nike MX ──────────────────────────────────────────────────────────────────

NIKE_PRODUCTOS = [
    ("Nike Air Max 270",        2499, 20, "tenis, running, nike"),
    ("Nike Revolution 6",       1299, 25, "tenis, running, nike"),
    ("Nike Dri-FIT Camiseta",    699, 30, "ropa deportiva, nike"),
    ("Nike Air Force 1",        1999, 20, "tenis, nike, casual"),
    ("Nike Zoom Pegasus",       2899, 15, "running, tenis, nike"),
    ("Nike Flex Experience",    1499, 25, "tenis, gym, nike"),
    ("Nike Pro Shorts",          599, 30, "ropa deportiva, nike, gym"),
    ("Nike Brasilia Mochila",    899, 20, "accesorios, nike"),
]

def run_nike():
    ofertas = []
    for nombre, precio, descuento, keywords in NIKE_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Nike MX",
            "tipo":            "moda",
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             "https://www.nike.com/mx/w/sale-3yaep",
            "tipo_promo":      f"-{descuento}% Sale Nike MX",
            "palabras_clave":  keywords,
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Nike MX] {len(ofertas)} ofertas")
    return ofertas

# ── Adidas MX ─────────────────────────────────────────────────────────────────

ADIDAS_PRODUCTOS = [
    ("Adidas Ultraboost 22",       3299, 25, "tenis, running, adidas"),
    ("Adidas Stan Smith",          1799, 20, "tenis, casual, adidas"),
    ("Adidas Superstar",           1599, 20, "tenis, casual, adidas"),
    ("Adidas Tiro Pants",           799, 30, "ropa deportiva, adidas, gym"),
    ("Adidas Forum Low",           1899, 20, "tenis, casual, adidas"),
    ("Adidas Entrada Jersey",       499, 35, "ropa deportiva, futbol, adidas"),
    ("Adidas Essentials Hoodie",    999, 25, "ropa, adidas, casual"),
    ("Adidas Predator Accuracy",  2499, 20, "tenis futbol, adidas"),
]

def run_adidas():
    ofertas = []
    for nombre, precio, descuento, keywords in ADIDAS_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Adidas MX",
            "tipo":            "moda",
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             "https://www.adidas.mx/sale",
            "tipo_promo":      f"-{descuento}% Sale Adidas MX",
            "palabras_clave":  keywords,
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Adidas MX] {len(ofertas)} ofertas")
    return ofertas

# ── Puma MX ───────────────────────────────────────────────────────────────────

PUMA_PRODUCTOS = [
    ("Puma Suede Classic XXI",  1299, 20, "tenis, casual, puma"),
    ("Puma RS-X",               1599, 25, "tenis, casual, puma"),
    ("Puma Camiseta Teamliga",   449, 30, "ropa, futbol, puma"),
    ("Puma Softride Enzo",      1199, 20, "tenis, running, puma"),
    ("Puma Essentials Hoodie",   799, 25, "ropa, casual, puma"),
]

def run_puma():
    ofertas = []
    for nombre, precio, descuento, keywords in PUMA_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Puma MX",
            "tipo":            "moda",
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             "https://mx.puma.com/es/sale",
            "tipo_promo":      f"-{descuento}% Sale Puma MX",
            "palabras_clave":  keywords,
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Puma MX] {len(ofertas)} ofertas")
    return ofertas

# ── Zara MX ───────────────────────────────────────────────────────────────────

ZARA_PRODUCTOS = [
    ("Zara Blazer Oversized", 1299, 30, "ropa, moda, zara, mujer",  "https://www.zara.com/mx/es/mujer-blazers-oversize-l4189.html"),
    ("Zara Jeans Slim",        799, 20, "pantalon, moda, zara",     "https://www.zara.com/mx/es/mujer-jeans-slim-l1280.html"),
    ("Zara Vestido Midi",      999, 25, "vestido, moda, zara, mujer","https://www.zara.com/mx/es/mujer-vestidos-midi-l1303.html"),
    ("Zara Camisa Oversize",   699, 30, "camisa, moda, zara",       "https://www.zara.com/mx/es/mujer-camisas-l1217.html"),
    ("Zara Zapatillas Piel",  1499, 20, "zapatos, moda, zara, mujer","https://www.zara.com/mx/es/mujer-zapatos-l1251.html"),
    ("Zara Bolso Tote",        899, 25, "bolsa, accesorios, zara",  "https://www.zara.com/mx/es/mujer-bolsos-tote-l1025.html"),
]

def run_zara():
    ofertas = []
    for nombre, precio, descuento, keywords, url in ZARA_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Zara MX",
            "tipo":            "moda",
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             url,
            "tipo_promo":      f"-{descuento}% Sale Zara MX",
            "palabras_clave":  keywords,
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Zara MX] {len(ofertas)} ofertas")
    return ofertas

# ── H&M MX ────────────────────────────────────────────────────────────────────

HM_PRODUCTOS = [
    ("H&M Vestido Floral",   499, 30, "vestido, moda, hm, mujer", "https://www2.hm.com/es_mx/mujer/productos/vestidos/vestidos-floral.html"),
    ("H&M Jeans Skinny",     599, 25, "pantalon, moda, hm",       "https://www2.hm.com/es_mx/mujer/productos/jeans/jeans-skinny.html"),
    ("H&M Camiseta Basica",  199, 30, "camiseta, moda, hm",       "https://www2.hm.com/es_mx/mujer/productos/camisetas-y-tops/camisetas.html"),
    ("H&M Sudadera Logo",    699, 20, "ropa, casual, hm",         "https://www2.hm.com/es_mx/mujer/productos/sudaderas-y-hoodies.html"),
    ("H&M Chaqueta Denim",   899, 25, "ropa, casual, hm",         "https://www2.hm.com/es_mx/mujer/productos/chaquetas-y-abrigos/chaquetas-denim.html"),
]

def run_hm():
    ofertas = []
    for nombre, precio, descuento, keywords, url in HM_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "H&M MX",
            "tipo":            "moda",
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             url,
            "tipo_promo":      f"-{descuento}% Sale H&M MX",
            "palabras_clave":  keywords,
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[H&M MX] {len(ofertas)} ofertas")
    return ofertas

