"""
agents/viajes.py — Viajes vía Awin — Agosto 2026
Trivago MX: MID 105931 (actualizado)
Sirenis Hotels: MID 109948 (actualizado)
Expedia MX: MID 117689
Hoteles.com MX: MID 117687
Kiwi: link existente
"""
from agents.base import AWIN_ID, precio_original, generar_fechas_viaje, ahora_str
from urllib.parse import quote

def awin_url(mid, destino):
    return (
        f"https://www.awin1.com/cread.php?"
        f"awinmid={mid}&awinaffid={AWIN_ID}"
        f"&ued={quote(destino, safe='')}"
    )

# ── Trivago MX — MID 105931 ───────────────────────────────────────────────────
TRIVAGO_DESTINOS = [
    ("Cancún, México",     1200, 20),
    ("Ciudad de México",    800, 15),
    ("Los Cabos",          1500, 25),
    ("Puerto Vallarta",    1100, 20),
    ("Playa del Carmen",   1300, 22),
    ("Tulum",              1400, 18),
    ("Oaxaca",              900, 15),
    ("Guadalajara",         850, 20),
]
def run_trivago():
    ofertas = []
    for i, (destino, precio, descuento) in enumerate(TRIVAGO_DESTINOS):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Trivago", "tipo": "viajes",
            "destino": f"Hotel en {destino}",
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN/noche",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("105931", f"https://www.trivago.com.mx/?search/200-{quote(destino)}"),
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "hotel, viaje, hospedaje, trivago",
            "fecha": ahora_str(), "activa": True,
        })
    print(f"[Trivago] {len(ofertas)} ofertas")
    return ofertas

# ── Kiwi MX ───────────────────────────────────────────────────────────────────
KIWI_VUELOS = [
    ("CDMX → Cancún",      1800, 15),
    ("CDMX → Los Cabos",   2100, 18),
    ("CDMX → Guadalajara",  900, 20),
    ("CDMX → Monterrey",    950, 15),
    ("CDMX → Miami",       4500, 22),
    ("CDMX → Nueva York",  5200, 20),
    ("CDMX → Madrid",      7800, 25),
    ("CDMX → Bogotá",      4200, 18),
]
def run_kiwi():
    ofertas = []
    for i, (ruta, precio, descuento) in enumerate(KIWI_VUELOS):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Kiwi", "tipo": "viajes",
            "destino": f"Vuelo {ruta}",
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig, "descuento_pct": descuento,
            "url": f"https://www.awin1.com/cread.php?s=2702014&v=20563&q=395852&r={AWIN_ID}",
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "vuelo, avion, kiwi, viaje",
            "fecha": ahora_str(), "activa": True,
        })
    print(f"[Kiwi] {len(ofertas)} ofertas")
    return ofertas

# ── Sirenis Hotels — MID 109948 ───────────────────────────────────────────────
SIRENIS_HOTELES = [
    ("Sirenis Punta Cana Resort — Todo Incluido", 3200, 25),
    ("Sirenis Riviera Maya — Todo Incluido",       2800, 20),
    ("Sirenis Tropical Suites Tenerife",           2500, 18),
]
def run_sirenis():
    ofertas = []
    for i, (nombre, precio, descuento) in enumerate(SIRENIS_HOTELES):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Sirenis Hotels", "tipo": "viajes", "destino": nombre,
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN/noche",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("109948", "https://www.sirenishotels.com/"),
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "hotel, resort, todo incluido, sirenis",
            "fecha": ahora_str(), "activa": True,
        })
    print(f"[Sirenis Hotels] {len(ofertas)} ofertas")
    return ofertas

# ── Expedia MX — MID 117689 ───────────────────────────────────────────────────
EXPEDIA_DESTINOS = [
    ("Cancún",          1350, 20), ("Los Cabos",        1800, 25),
    ("Puerto Vallarta", 1250, 18), ("Ciudad de México",  950, 15),
    ("Playa del Carmen",1450, 22), ("Tulum",            1600, 20),
    ("Oaxaca",          1050, 15), ("Guadalajara",       980, 18),
]
def run_expedia():
    ofertas = []
    for i, (destino, precio, descuento) in enumerate(EXPEDIA_DESTINOS):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Expedia MX", "tipo": "viajes",
            "destino": f"Hotel en {destino} — Expedia",
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN/noche",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("117689", "https://www.expedia.mx/Hotels"),
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "hotel, viaje, hospedaje, expedia",
            "fecha": ahora_str(), "activa": True,
        })
    print(f"[Expedia MX] {len(ofertas)} ofertas")
    return ofertas

# ── Hoteles.com MX — MID 117687 ──────────────────────────────────────────────
HOTELES_DESTINOS = [
    ("Cancún",          1300, 20), ("Los Cabos",        1750, 22),
    ("Puerto Vallarta", 1200, 18), ("Ciudad de México",  900, 15),
    ("Playa del Carmen",1400, 20), ("Tulum",            1550, 25),
    ("Oaxaca",          1000, 15), ("Monterrey",         950, 18),
]
def run_hoteles():
    ofertas = []
    for i, (destino, precio, descuento) in enumerate(HOTELES_DESTINOS):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Hoteles.com MX", "tipo": "viajes",
            "destino": f"Hotel en {destino} — Hoteles.com",
            "precio": precio, "precio_fmt": f"${precio:,.0f} MXN/noche",
            "precio_original": orig, "descuento_pct": descuento,
            "url": awin_url("117687", "https://www.hoteles.com/"),
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "hotel, viaje, hospedaje, hoteles.com",
            "fecha": ahora_str(), "activa": True,
        })
    print(f"[Hoteles.com MX] {len(ofertas)} ofertas")
    return ofertas

def run():
    ofertas = []
    ofertas.extend(run_trivago())
    ofertas.extend(run_kiwi())
    ofertas.extend(run_sirenis())
    ofertas.extend(run_expedia())
    ofertas.extend(run_hoteles())
    print(f"[Viajes total] {len(ofertas)} ofertas")
    return ofertas
