"""
agents/mercadolibre.py — Agente Mercado Libre (API oficial MLM)
Único agente con precios 100% reales en tiempo real desde el día 1.
"""
import requests
from agents.base import PRECIO_MAX_MXN, ahora_str

BUSQUEDAS = [
    ("laptop",          "electronico"),
    ("iphone",          "electronico"),
    ("samsung galaxy",  "electronico"),
    ("tenis nike",      "moda"),
    ("tenis adidas",    "moda"),
    ("television 4k",   "electronico"),
    ("audifonos",       "electronico"),
    ("refrigerador",    "hogar"),
    ("perfume",         "belleza"),
    ("nintendo switch", "electronico"),
]

def run():
    ofertas = []
    for query, tipo in BUSQUEDAS:
        try:
            url = (
                f"https://api.mercadolibre.com/sites/MLM/search"
                f"?q={requests.utils.quote(query)}&sort=relevance&limit=5"
            )
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                print(f"[MercadoLibre] HTTP {r.status_code} para '{query}'")
                continue
            for item in r.json().get("results", []):
                precio    = item.get("price", 0)
                original  = item.get("original_price") or 0
                if not (200 <= precio <= PRECIO_MAX_MXN):
                    continue
                if original <= precio:
                    continue
                descuento = round((1 - precio / original) * 100)
                if descuento < 5:
                    continue
                ofertas.append({
                    "fuente":          "Mercado Libre",
                    "tipo":            tipo,
                    "destino":         item["title"][:80],
                    "precio":          precio,
                    "precio_fmt":      f"${precio:,.0f} MXN",
                    "precio_original": round(original),
                    "descuento_pct":   descuento,
                    "url":             item["permalink"],
                    "tipo_promo":      f"-{descuento}% descuento",
                    "palabras_clave":  query,
                    "fecha":           ahora_str(),
                    "activa":          True,
                })
        except Exception as e:
            print(f"[MercadoLibre] Error '{query}': {e}")
    print(f"[Mercado Libre] {len(ofertas)} ofertas")
    return ofertas

