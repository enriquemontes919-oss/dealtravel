"""
agents/xcaret.py — Agente Xcaret (Awin aprobado)
Deep links via Awin ID 2876425, Advertiser ID 34947
"""
from urllib.parse import quote
from agents.base import AWIN_ID, precio_original, generar_fechas_viaje, ahora_str

AWIN_MID_XCARET = "34947"

def xcaret_url(path):
    base = f"https://www.xcaret.com{path}"
    return (
        f"https://www.awin1.com/cread.php?"
        f"awinmid={AWIN_MID_XCARET}&awinaffid={AWIN_ID}"
        f"&ued={quote(base, safe='')}"
    )

PRODUCTOS = [
    ("Xcaret — Parque Eco-Arqueológico",          2100, 20, "/es/xcaret-park/"),
    ("Xel-Há — Todo Incluido",                    2400, 25, "/es/xel-ha-park/"),
    ("Xplor — Aventura y Tirolesas",              2200, 20, "/es/xplor-park/"),
    ("Xoximilco — Fiesta Mexicana Todo Incluido", 1800, 15, "/es/xoximilco/"),
    ("Xenses — Parque de los Sentidos",           1500, 20, "/es/xenses-park/"),
    ("Xenotes — Oasis Maya",                      2000, 18, "/es/xenotes/"),
    ("Xavage — Parque Extremo",                   1900, 20, "/es/xavage/"),
    ("Xcaret Arte — Espectáculo Nocturno",         1600, 15, "/es/xcaret-arte/"),
    ("Hotel Xcaret México — Todo Incluido",        8500, 25, "/es/hotel-xcaret-mexico/"),
    ("Hotel Xcaret Arte — Solo Adultos",           9500, 20, "/es/hotel-xcaret-arte/"),
    ("Xcaretplus — 2 Parques + Traslado",          3800, 22, "/es/xcaretplus/"),
    ("Paquete Familia Xcaret + Xel-Há",            7200, 25, "/es/paquetes/"),
]

def run():
    ofertas = []
    for i, (nombre, precio, descuento, path) in enumerate(PRODUCTOS):
        orig   = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente":          "Xcaret",
            "tipo":            "viajes",
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             xcaret_url(path),
            "tipo_promo":      f"-{descuento}% Oferta Xcaret · {fechas}",
            "palabras_clave":  "xcaret, parque, viaje, cancun, riviera maya, todo incluido",
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Xcaret] {len(ofertas)} ofertas")
    return ofertas
