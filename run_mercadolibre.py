"""
run_mercadolibre.py — Entry point para GitHub Actions
Usa Access Token oficial de ML para búsquedas autenticadas
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://zutcsoloxabwtrvfzmlm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_5TNTtixQcRsdbS_kmojIOA_6TNjtiLT")

ML_CLIENT_ID     = "8811685687859386"
ML_CLIENT_SECRET = "rPuY0Q2oPlXqZZlVdw40kQ2xFU205DjZ"
ML_REFRESH_TOKEN = os.getenv("ML_REFRESH_TOKEN", "")
ML_ACCESS_TOKEN  = os.getenv("ML_ACCESS_TOKEN", "APP_USR-8811685687859386-052818-379beb12c596da7542b8762d42a67ba3-3434595846")

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

PRECIO_MAX_MXN = 50000

def scrape_ml(token):
    ofertas = []
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    for query, tipo in BUSQUEDAS:
        try:
            url = (
                f"https://api.mercadolibre.com/sites/MLM/search"
                f"?q={requests.utils.quote(query)}&sort=relevance&limit=8"
            )
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f"[ML] HTTP {r.status_code} para '{query}'")
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
                    "fecha":           datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "activa":          True,
                })
            print(f"[ML] '{query}' procesado")
        except Exception as e:
            print(f"[ML] Error '{query}': {e}")
    print(f"[ML] {len(ofertas)} ofertas con descuento encontradas")
    return ofertas

def guardar_en_supabase(ofertas):
    hdrs = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "return=minimal"
    }
    requests.delete(
        f"{SUPABASE_URL}/rest/v1/ofertas?fuente=eq.Mercado%20Libre",
        headers=hdrs, timeout=10
    )
    print("[ML] Ofertas anteriores eliminadas")
    nuevas = 0
    for oferta in ofertas:
        try:
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/ofertas",
                headers=hdrs, json=oferta, timeout=10
            )
            if r.status_code in [200, 201]:
                nuevas += 1
        except Exception as e:
            print(f"[ML] Error guardando: {e}")
    print(f"[ML] {nuevas} ofertas guardadas en Supabase")

if __name__ == "__main__":
    print("=" * 50)
    print(f"ML SCRAPER — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 50)
    ofertas = scrape_ml(ML_ACCESS_TOKEN)
    guardar_en_supabase(ofertas)
    print("DONE")
