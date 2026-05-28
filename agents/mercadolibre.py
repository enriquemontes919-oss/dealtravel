"""
agents/mercadolibre.py — Agente Mercado Libre vía Scraperapi Proxy
Usa proxy HTTP de Scraperapi en lugar del endpoint API
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

def run():
    ofertas = []

    if not SCRAPERAPI_KEY:
        print("[MercadoLibre] Sin SCRAPERAPI_KEY — saltando agente")
        return ofertas

    # Proxy de Scraperapi — evita el bloqueo de IP de Railway
    proxies = {
        "http":  f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
        "https": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    for query, tipo in BUSQUEDAS:
        try:
            url = (
                f"https://api.mercadolibre.com/sites/MLM/search"
                f"?q={requests.utils.quote(query)}&sort=relevance&limit=8"
            )
            r = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                verify=False,
                timeout=30
            )
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
