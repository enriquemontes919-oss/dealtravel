"""
scraper.py — Orquestador principal de DealTravel
Railway lo ejecuta como cron (0 * * * *) cada hora y lo termina al finalizar.
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from agents.amazon       import run as run_amazon
from agents.mercadolibre import run as run_mercadolibre
from agents.moda         import run_nike, run_adidas, run_puma, run_zara, run_hm
from agents.viajes       import run as run_viajes
from agents.xcaret       import run as run_xcaret
from agents.liverpool    import run as run_liverpool
from agents.palacio      import run as run_palacio
from agents.alertas      import revisar_alertas
from agents.base         import SUPABASE_URL, SUPABASE_KEY, supabase_headers

TIENDAS_FIJAS = [
    "Nike MX", "Adidas MX", "Puma MX", "Zara MX", "H&M MX",
    "Trivago", "Kiwi", "Sirenis Hotels", "Amazon MX",
    "Expedia MX", "Hoteles.com MX", "Xcaret",
    "Liverpool", "Palacio de Hierro",
]

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

def limpiar_tiendas_fijas(ofertas):
    hdrs = supabase_headers()
    fuentes_fijas = set(o["fuente"] for o in ofertas if o["fuente"] in TIENDAS_FIJAS)
    for fuente in fuentes_fijas:
        try:
            fuente_enc = requests.utils.quote(fuente)
            requests.delete(
                f"{SUPABASE_URL}/rest/v1/ofertas?fuente=eq.{fuente_enc}",
                headers={**hdrs, "Prefer": "return=minimal"}, timeout=10
            )
            print(f"[Supabase] Limpieza previa: {fuente}")
        except Exception as e:
            print(f"[Supabase] Error limpiando {fuente}: {e}")

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

def guardar_en_supabase(ofertas):
    hdrs = {**supabase_headers(), "Prefer": "return=minimal"}
    limpiar_tiendas_fijas(ofertas)
    nuevas = 0
    for oferta in ofertas:
        try:
            es_fija = oferta["fuente"] in TIENDAS_FIJAS
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

def monitorear():
    print("=" * 55)
    print(f"DEAL TRAVEL AGENTES — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 55)

    marcar_inactivas_viejas()

    todas = []
    todas.extend(run_amazon())
    todas.extend(run_mercadolibre())
    todas.extend(run_nike())
    todas.extend(run_adidas())
    todas.extend(run_puma())
    todas.extend(run_zara())
    todas.extend(run_hm())
    todas.extend(run_viajes())
    todas.extend(run_xcaret())
    todas.extend(run_liverpool())
    todas.extend(run_palacio())

    print(f"\nTOTAL encontradas: {len(todas)}")
    guardar_en_supabase(todas)

    # IMPORTANTE: pasar `todas` directamente a revisar_alertas
    # evita releer Supabase y garantiza que el matching use
    # exactamente las mismas ofertas recién insertadas
    revisar_alertas(todas)

    print("=" * 55)
    print("DONE — Railway puede terminar el proceso")
    print("=" * 55)

if __name__ == "__main__":
    monitorear()
