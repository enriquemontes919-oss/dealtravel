"""
agents/moda.py — Moda y tecnología con Awin aprobado — Agosto 2026
Nike MX: MID 117547
Lacoste MX: MID 32585
Honor MX: MID 50221
LaserPecker: MID 59557
SmartBuyGlasses MX: MID 128565
Golden Maple: MID 124092
"""
from agents.base import AWIN_ID, precio_original, ahora_str
from urllib.parse import quote

def awin_url(mid, destino):
    return (
        f"https://www.awin1.com/cread.php?"
        f"awinmid={mid}&awinaffid={AWIN_ID}"
        f"&ued={quote(destino, safe='')}"
    )

# ── Nike MX — MID 117547 ─────────────────────────────────────────────────────
NIKE_PRODUCTOS = [
    ("Nike Air Max 270",      2499, 20, "tenis, running, nike"),
    ("Nike Revolution 6",     1299, 25, "tenis, running, nike"),
    ("Nike Dri-FIT Camiseta",  699, 30, "ropa deportiva, nike"),
    ("Nike Air Force 1",      1999, 20, "tenis, nike, casual"),
    ("Nike Zoom Pegasus",     2899, 15, "running, tenis, nike"),
    ("Nike Flex Experience",  1499, 25, "tenis, gym, nike"),
    ("Nike Pro Shorts",        599, 30, "ropa deportiva, nike, gym"),
    ("Nike Brasilia Mochila",  899, 20, "accesorios, nike"),
]
def run_nike():
    ofertas = []
    for nombre, precio, descuento, keywords in NIKE_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "Nike MX", "tipo": "moda", "destino": nombre,
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("117547", "https://www.nike.com/mx/w/sale-3yaep"),
            "tipo_promo": f"-{descuento}% Sale Nike MX",
            "palabras_clave": keywords, "fecha": ahora_str(), "activa": True,
        })
    print(f"[Nike MX] {len(ofertas)} ofertas")
    return ofertas

# ── Lacoste MX — MID 32585 ───────────────────────────────────────────────────
LACOSTE_PRODUCTOS = [
    ("Lacoste Polo Classic Fit Hombre",  2299, 20, "polo, ropa, lacoste, hombre"),
    ("Lacoste Polo Slim Fit Mujer",      2099, 20, "polo, ropa, lacoste, mujer"),
    ("Lacoste Tenis L-Spin Hombre",      2799, 25, "tenis, casual, lacoste"),
    ("Lacoste Tenis Lerond Mujer",       2599, 20, "tenis, casual, lacoste"),
    ("Lacoste Chamarra Blouson Hombre",  3999, 25, "chamarra, ropa, lacoste"),
    ("Lacoste Bolsa Concept Mujer",      3499, 30, "bolsa, accesorios, lacoste"),
    ("Lacoste Sudadera Full Zip Hombre", 2799, 20, "sudadera, ropa, lacoste"),
    ("Lacoste Perfume L.12.12 Blanc",    1899, 15, "perfume, fragancia, lacoste"),
]
def run_lacoste():
    ofertas = []
    for nombre, precio, descuento, keywords in LACOSTE_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "Lacoste MX", "tipo": "moda", "destino": nombre,
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("32585", "https://www.lacoste.com/mx/es/outlet/"),
            "tipo_promo": f"-{descuento}% Outlet Lacoste MX",
            "palabras_clave": keywords, "fecha": ahora_str(), "activa": True,
        })
    print(f"[Lacoste MX] {len(ofertas)} ofertas")
    return ofertas

# ── Honor MX — MID 50221 ─────────────────────────────────────────────────────
HONOR_PRODUCTOS = [
    ("Honor Magic7 Pro 5G",          14999, 20, "celular, smartphone, honor"),
    ("Honor X8b 256GB",               5999, 25, "celular, smartphone, honor"),
    ("Honor Pad 9 12.1\"",            7499, 20, "tablet, honor"),
    ("Honor MagicWatch 4",            3999, 25, "smartwatch, reloj, honor"),
    ("Honor Earbuds X7",              1299, 30, "audifonos, honor, earbuds"),
    ("Honor Magic V3 Plegable",      29999, 15, "celular, plegable, honor"),
    ("Honor 200 Lite 5G",             5499, 20, "celular, smartphone, honor"),
    ("Honor Band 9",                  1199, 25, "smartband, pulsera, honor"),
]
def run_honor():
    ofertas = []
    for nombre, precio, descuento, keywords in HONOR_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "Honor MX", "tipo": "electronico", "destino": nombre,
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("50221", "https://www.honor.com/mx/shop/"),
            "tipo_promo": f"-{descuento}% Oferta Honor MX",
            "palabras_clave": keywords, "fecha": ahora_str(), "activa": True,
        })
    print(f"[Honor MX] {len(ofertas)} ofertas")
    return ofertas

# ── LaserPecker — MID 59557 ──────────────────────────────────────────────────
LASERPECKER_PRODUCTOS = [
    ("LaserPecker 4 Grabadora Láser Dual",  15999, 20, "grabadora, laser, laserpecker"),
    ("LaserPecker 2 Pro Grabadora Portátil", 8999, 25, "grabadora, laser, laserpecker"),
    ("LaserPecker 3 Fibra Óptica",          12999, 20, "grabadora, laser, fibra, laserpecker"),
    ("LaserPecker LX1 Mini Cortadora",       5999, 30, "cortadora, laser, laserpecker"),
    ("LaserPecker Filamento PLA 1kg",          799, 20, "filamento, impresora, laserpecker"),
    ("LaserPecker Honeycomb Panel",           1299, 25, "accesorio, grabadora, laserpecker"),
]
def run_laserpecker():
    ofertas = []
    for nombre, precio, descuento, keywords in LASERPECKER_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "LaserPecker", "tipo": "electronico", "destino": nombre,
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("59557", "https://global.laserpecker.net/es"),
            "tipo_promo": f"-{descuento}% Oferta LaserPecker",
            "palabras_clave": keywords, "fecha": ahora_str(), "activa": True,
        })
    print(f"[LaserPecker] {len(ofertas)} ofertas")
    return ofertas

# ── SmartBuyGlasses MX — MID 128565 ─────────────────────────────────────────
SBG_PRODUCTOS = [
    ("Ray-Ban Wayfarer Clásico",         2999, 30, "lentes, ray-ban, smartbuyglasses"),
    ("Oakley Holbrook Polarizado",        3499, 25, "lentes, oakley, smartbuyglasses"),
    ("Ray-Ban Aviator Gradient",          2799, 30, "lentes, ray-ban, smartbuyglasses"),
    ("Tom Ford Rectangular Hombre",       5999, 20, "lentes, tom ford, smartbuyglasses"),
    ("Persol PO3019S Italiano",           4499, 25, "lentes, persol, smartbuyglasses"),
    ("Carrera Speedway Deportivo",        2499, 30, "lentes, carrera, smartbuyglasses"),
    ("Prada SPR 17W Mujer",              5499, 20, "lentes, prada, smartbuyglasses"),
    ("Gucci GG0062S Mujer",              6499, 25, "lentes, gucci, smartbuyglasses"),
]
def run_smartbuyglasses():
    ofertas = []
    for nombre, precio, descuento, keywords in SBG_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "SmartBuyGlasses MX", "tipo": "moda", "destino": nombre,
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("128565", "https://es.smartbuyglasses.com/"),
            "tipo_promo": f"-{descuento}% Oferta SmartBuyGlasses",
            "palabras_clave": keywords, "fecha": ahora_str(), "activa": True,
        })
    print(f"[SmartBuyGlasses MX] {len(ofertas)} ofertas")
    return ofertas

# ── Golden Maple — MID 124092 ────────────────────────────────────────────────
GOLDENMAPLE_PRODUCTOS = [
    ("Golden Maple Set Pinceles Miniatura 15pz",   899, 25, "pinceles, pintura, golden maple, arte"),
    ("Golden Maple Pincel Detalle Ultra Fino",      299, 30, "pincel, arte, miniatura, golden maple"),
    ("Golden Maple Set Acuarelas 36 Colores",       799, 20, "acuarelas, pintura, golden maple"),
    ("Golden Maple Pinceles Gouache Premium",        599, 25, "pinceles, gouache, arte, golden maple"),
    ("Golden Maple Kit Iniciación Miniatura",       1299, 20, "kit, pintura, miniatura, golden maple"),
    ("Golden Maple Paleta Mezcla Porcelana",         349, 30, "paleta, pintura, arte, golden maple"),
]
def run_goldenmaple():
    ofertas = []
    for nombre, precio, descuento, keywords in GOLDENMAPLE_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "Golden Maple", "tipo": "hogar", "destino": nombre,
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("124092", "https://artgoldenmaple.com/collections/miniature-brush"),
            "tipo_promo": f"-{descuento}% Oferta Golden Maple",
            "palabras_clave": keywords, "fecha": ahora_str(), "activa": True,
        })
    print(f"[Golden Maple] {len(ofertas)} ofertas")
    return ofertas
