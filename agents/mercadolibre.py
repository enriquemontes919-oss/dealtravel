"""
agents/mercadolibre.py — Agente Mercado Libre vía Scraperapi
Resuelve el bloqueo de IP de Railway usando proxy de Scraperapi
"""
import os
import time
import random
import requests
from agents.base import PRECIO_MAX_MXN, ahora_str

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY", "")

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
    ("playstation",     "electronico"),
    ("smartwatch",      "electronico"),
]

def scraper_url(target_url):
    from urllib.parse import quote
    return (
        f"https://api.scraperapi.com"
        f"?api_key={SCRAPERAPI_KEY}"
        f"&url={quote(target_url, safe='')}"
    )

def run():
    ofertas = []

    if not SCRAPERAPI_KEY:
        print("[MercadoLibre] Sin SCRAPERAPI_KEY — saltando agente")
        return ofertas

    for query, tipo in BUSQUEDAS:
        try:
            ml_url = (
                f"https://api.mercadolibre.com/sites/MLM/search"
                f"?q={requests.utils.quote(query)}&sort=relevance&limit=8"
            )
            r = requests.get(scraper_url(ml_url), timeout=30)
            if r.status_code != 200:
                print(f"[MercadoLibre] HTTP {r.status_code} para '{query}'")
                time.sleep(random.uniform(2, 4))
                continue

            resultados = r.json().get("results", [])
            for item in resultados:
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

            print(f"[MercadoLibre] '{query}' → {len(resultados)} resultados")
            time.sleep(random.uniform(1.0, 2.0))

        except Exception as e:
            print(f"[MercadoLibre] Error '{query}': {e}")

    print(f"[Mercado Libre] {len(ofertas)} ofertas con descuento encontradas")
    return ofertas
