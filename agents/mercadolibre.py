"""
agents/mercadolibre.py — Agente Mercado Libre (API oficial MLM)
Único agente con precios 100% reales en tiempo real desde el día 1.
"""
import time
import random
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

# Headers que simulan un navegador real — evita el 403
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
    "Referer":         "https://www.mercadolibre.com.mx/",
    "Origin":          "https://www.mercadolibre.com.mx",
}

def run():
    ofertas = []
    for query, tipo in BUSQUEDAS:
        try:
            url = (
                f"https://api.mercadolibre.com/sites/MLM/search"
                f"?q={requests.utils.quote(query)}&sort=relevance&limit=8"
            )
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"[MercadoLibre] HTTP {r.status_code} para '{query}'")
                time.sleep(random.uniform(3, 6))
                continue

            for item in r.json().get("results", []):
                precio   = item.get("price", 0)
                original = item.get("original_price") or 0
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

            # Delay entre búsquedas para no ser bloqueados
            time.sleep(random.uniform(1.5, 3.0))

        except Exception as e:
            print(f"[MercadoLibre] Error '{query}': {e}")

    print(f"[Mercado Libre] {len(ofertas)} ofertas")
    return ofertas
