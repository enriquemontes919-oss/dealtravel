"""
agents/palacio.py — Agente El Palacio de Hierro
URLs verificadas desde Google Search — Mayo 2026
Estructura: elpalaciodehierro.com/seccion/categoria/
"""
from agents.base import precio_original, ahora_str

PALACIO_PRODUCTOS = [
    # Moda mujer
    ("Palacio — Bolsa Michael Kors Jet Set Piel",      4999, 30, "moda",
     "https://www.elpalaciodehierro.com/mujer/bolsos-y-carteras/"),
    ("Palacio — Vestido Ralph Lauren Midi Mujer",      4799, 30, "moda",
     "https://www.elpalaciodehierro.com/mujer/ropa/vestidos/"),
    ("Palacio — Chamarra Calvin Klein Mujer",          3499, 25, "moda",
     "https://www.elpalaciodehierro.com/mujer/ropa/chamarras-y-abrigos/"),
    ("Palacio — Tenis Prada Downtown Mujer",          14999, 20, "moda",
     "https://www.elpalaciodehierro.com/mujer/zapatos/tenis/"),
    # Moda hombre
    ("Palacio — Tenis Gucci Rhython Hombre",          18999, 20, "moda",
     "https://www.elpalaciodehierro.com/hombre/zapatos/tenis/"),
    ("Palacio — Cartera Coach Para Hombre Piel",       2199, 30, "moda",
     "https://www.elpalaciodehierro.com/hombre/accesorios/carteras/"),
    ("Palacio — Reloj Fossil Automático Hombre",       3499, 25, "moda",
     "https://www.elpalaciodehierro.com/hombre/accesorios/relojes/"),
    # Belleza / perfumes
    ("Palacio — Perfume Chanel No.5 EDP 100ml",        4999, 15, "belleza",
     "https://www.elpalaciodehierro.com/belleza/fragancias/para-ella/"),
    ("Palacio — Perfume YSL Libre EDP 90ml",           3899, 20, "belleza",
     "https://www.elpalaciodehierro.com/belleza/fragancias/para-ella/"),
    ("Palacio — Set Skincare La Mer Hidratante",        8999, 25, "belleza",
     "https://www.elpalaciodehierro.com/belleza/cuidado-de-la-piel/"),
    ("Palacio — Crema Facial Clinique Hidratante 50ml",  899, 20, "belleza",
     "https://www.elpalaciodehierro.com/belleza/cuidado-de-la-piel/"),
    # Accesorios / viaje
    ("Palacio — Maleta Samsonite Spinner 24\" Hardside", 3999, 30, "hogar",
     "https://www.elpalaciodehierro.com/mujer/bolsos-y-carteras/maletas-y-equipaje/"),
]

def run():
    ofertas = []
    for nombre, precio, descuento, tipo, url in PALACIO_PRODUCTOS:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente":          "Palacio de Hierro",
            "tipo":            tipo,
            "destino":         nombre,
            "precio":          precio,
            "precio_fmt":      f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct":   descuento,
            "url":             url,
            "tipo_promo":      f"-{descuento}% Oferta Palacio de Hierro",
            "palabras_clave":  nombre.lower(),
            "fecha":           ahora_str(),
            "activa":          True,
        })
    print(f"[Palacio de Hierro] {len(ofertas)} ofertas")
    return ofertas
