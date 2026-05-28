"""
agents/mercadolibre.py — Agente Mercado Libre con Access Token oficial
Client Credentials flow — no requiere intervención del usuario
"""
import time
import random
import requests
from agents.base import PRECIO_MAX_MXN, ahora_str

ML_CLIENT_ID     = "8811685687859386"
ML_CLIENT_SECRET = "rPuY0Q2oPlXqZZlVdw40kQ2xFU205DjZ"

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

def obtener_access_token():
    """Obtiene Access Token via Client Credentials — no requiere login de usuario"""
    try:
        r = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type":    "client_credentials",
                "client_id":     ML_CLIENT_ID,
                "client_secret": ML_CLIENT_SECRET,
            },
            timeout=15
        )
        if r.status_code == 200:
            token = r.json().get("access_token")
            print(f"[MercadoLibre] Access Token obtenido ✓")
            return token
        else:
            print(f"[MercadoLibre] Error obteniendo token: {r.status_code} — {r.text[:100]}")
            return None
    except Exception as e:
        print(f"[MercadoLibre] Error token: {e}")
        return None

def run():
    ofertas = []

    token = obtener_access_token()
    if not token:
        print("[MercadoLibre] Sin token — saltando agente")
        return ofertas

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept":        "application/json",
    }

    for query, tipo in BUSQUEDAS:
        try:
            url = (
                f"https://api.mercadolibre.com/sites/MLM/search"
                f"?q={requests.utils.quote(query)}&sort=relevance&limit=8"
            )
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f"[MercadoLibre] HTTP {r.status_code} para '{query}'")
                time.sleep(random.uniform(2, 4))
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

            # Delay entre búsquedas
            time.sleep(random.uniform(1.0, 2.0))

        except Exception as e:
            print(f"[MercadoLibre] Error '{query}': {e}")

    print(f"[Mercado Libre] {len(ofertas)} ofertas")
    return ofertas
