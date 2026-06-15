"""
agents/moda.py — Agentes de moda: Nike MX y Lacoste MX
Solo anunciantes aprobados en Awin — Junio 2026
Nike MX: MID 117547 ✅
Lacoste MX: MID 32585 ✅
Quitados: Adidas, Puma, Zara, H&M (sin aprobación Awin)
"""
from agents.base import AWIN_ID, precio_original, ahora_str
from urllib.parse import quote

AWIN_MID_NIKE    = "117547"
AWIN_MID_LACOSTE = "32585"

def nike_url(path="/mx/w/sale-3yaep"):
    destino = f"https://www.nike.com{path}"
    return (
        f"https://www.awin1.com/cread.php?"
        f"awinmid={AWIN_MID_NIKE}&awinaffid={AWIN_ID}"
        f"&ued={quote(destino, safe='')}"
    )

def lacoste_url(path="/mx/es/outlet/"):
    destino = f"https://www.lacoste.com{path}"
    return (
        f"https://www.awin1.com/cread.php?"
        f"awinmid={AWIN_MID_LACOSTE}&awinaffid={AWIN_ID}"
        f"&ued={quote(destino, safe='')}"
    )

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
            "url":             nike_url(),
            "tipo_promo":      f"-{descuento}% Sale Nike MX",
            "palabras_clave":  keywords,
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Nike MX] {len(ofertas)} ofertas")
    return ofertas

# ── Lacoste MX ───────────────────────────────────────────────────────────────

LACOSTE_PRODUCTOS = [
    ("Lacoste Polo Classic Fit Hombre",    2299, 20, "polo, ropa, lacoste, hombre"),
    ("Lacoste Polo Slim Fit Mujer",        2099, 20, "polo, ropa, lacoste, mujer"),
    ("Lacoste Tenis L-Spin Hombre",        2799, 25, "tenis, casual, lacoste"),
    ("Lacoste Tenis Lerond Mujer",         2599, 20, "tenis, casual, lacoste"),
    ("Lacoste Chamarra Blouson Hombre",    3999, 25, "chamarra, ropa, lacoste"),
    ("Lacoste Bolsa Concept Mujer",        3499, 30, "bolsa, accesorios, lacoste"),
    ("Lacoste Sudadera Full Zip Hombre",   2799, 20, "sudadera, ropa, lacoste"),
    ("Lacoste Perfume L.12.12 Blanc",      1899, 15, "perfume, fragancia, lacoste"),
]

def run_lacoste():
    ofertas = []
    for nombre, precio, descuento, keywords in LACOSTE_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Lacoste MX",
            "tipo":            "moda",
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             lacoste_url(),
            "tipo_promo":      f"-{descuento}% Outlet Lacoste MX",
            "palabras_clave":  keywords,
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Lacoste MX] {len(ofertas)} ofertas")
    return ofertas
