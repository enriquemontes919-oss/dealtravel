"""
scraper.py — Orquestador principal de DealTravel
Railway lo ejecuta como cron (0 * * * *) cada hora y lo termina al finalizar.
NO usa schedule ni while True — Railway maneja el timing.
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Importar agentes
from agents.amazon       import run as run_amazon
from agents.mercadolibre import run as run_mercadolibre
from agents.moda         import run_nike, run_adidas, run_puma, run_zara, run_hm
from agents.viajes       import run as run_viajes
from agents.alertas      import revisar_alertas
from agents.base         import SUPABASE_URL, SUPABASE_KEY, supabase_headers

TIENDAS_FIJAS = [
    "Nike MX", "Adidas MX", "Puma MX", "Zara MX", "H&M MX",
    "Trivago", "Kiwi", "Sirenis Hotels", "Amazon MX",
    "Expedia MX", "Hoteles.com MX",
]

# ── Supabase helpers ──────────────────────────────────────────────────────────

def oferta_ya_existe(destino, precio, fuente):
    try:
        term = requests.utils.quote(destino[:25])
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/ofertas"
            f"?destino=ilike.*{term}*&precio=eq.{precio}&fuente=eq.{fuente}",
            headers=supabase_headers(), timeout=10
        )
        return len(r.json()) > 0
    except:
        return False

def marcar_inactivas_viejas():
    hdrs = supabase_headers()
    todas_tiendas = TIENDAS_FIJAS + ["Mercado Libre"]
    for tienda in todas_tiendas:
        try:
            tienda_enc = requests.utils.quote(tienda)
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/ofertas"
                f"?fuente=eq.{tienda_enc}&activa=eq.true&select=id,fecha",
                headers=hdrs, timeout=10
            )
            for item in r.json():
                try:
                    fecha_oferta = datetime.strptime(item["fecha"], "%d/%m/%Y %H:%M")
                    if datetime.now() - fecha_oferta > timedelta(days=7):
                        requests.patch(
                            f"{SUPABASE_URL}/rest/v1/ofertas?id=eq.{item['id']}",
                            headers={**hdrs, "Prefer": "return=minimal"},
                            json={"activa": False}, timeout=10
                        )
                except:
                    pass
        except Exception as e:
            print(f"[Supabase] Error limpieza {tienda}: {e}")
    print("[Supabase] Ofertas viejas marcadas como inactivas")

def limpiar_tiendas_fijas(ofertas):
    """Borra ofertas anteriores de tiendas fijas antes de reinsertar.
    Así nunca se acumulan duplicados por reinserción horaria."""
    hdrs = supabase_headers()
    fuentes_fijas = set(o["fuente"] for o in ofertas if o["fuente"] in TIENDAS_FIJAS)
    for fuente in fuentes_fijas:
        try:
            fuente_enc = requests.utils.quote(fuente)
            r = requests.delete(
                f"{SUPABASE_URL}/rest/v1/ofertas?fuente=eq.{fuente_enc}",
                headers={**hdrs, "Prefer": "return=minimal"}, timeout=10
            )
            print(f"[Supabase] Limpieza previa: {fuente}")
        except Exception as e:
            print(f"[Supabase] Error limpiando {fuente}: {e}")

def guardar_en_supabase(ofertas):
    hdrs = {**supabase_headers(), "Prefer": "return=minimal"}

    # Primero limpiar tiendas fijas para evitar duplicados
    limpiar_tiendas_fijas(ofertas)

    nuevas = 0
    for oferta in ofertas:
        try:
            es_fija = oferta["fuente"] in TIENDAS_FIJAS
            # Tiendas fijas: siempre insertar (ya limpiamos antes)
            # Mercado Libre: solo insertar si no existe (tiene productos únicos reales)
            if es_fija or not oferta_ya_existe(oferta["destino"], oferta["precio"], oferta["fuente"]):
                r = requests.post(
                    f"{SUPABASE_URL}/rest/v1/ofertas",
                    headers=hdrs, json=oferta, timeout=10
                )
                if r.status_code in [200, 201]:
                    nuevas += 1
        except Exception as e:
            print(f"[Supabase] Error guardando oferta: {e}")
    print(f"[Supabase] {nuevas} ofertas guardadas (de {len(ofertas)} encontradas)")

# ── Orquestador ───────────────────────────────────────────────────────────────

def monitorear():
    print("=" * 55)
    print(f"DEAL TRAVEL AGENTES — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 55)

    marcar_inactivas_viejas()

    # Correr todos los agentes
    todas = []
    todas.extend(run_amazon())
    todas.extend(run_mercadolibre())
    todas.extend(run_nike())
    todas.extend(run_adidas())
    todas.extend(run_puma())
    todas.extend(run_zara())
    todas.extend(run_hm())
    todas.extend(run_viajes())

    print(f"\nTOTAL encontradas: {len(todas)}")
    guardar_en_supabase(todas)
    revisar_alertas(todas)

    print("=" * 55)
    print("DONE — Railway puede terminar el proceso")
    print("=" * 55)

if __name__ == "__main__":
    monitorear()
    # Sin schedule ni while True — Railway cron se encarga del timing
