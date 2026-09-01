"""
scraper.py — Orquestador DealTravel — Agosto 2026
Anunciantes Awin activos:
Nike MX (117547), Lacoste MX (32585), Honor MX (50221),
LaserPecker (59557), SmartBuyGlasses MX (128565), Golden Maple (124092),
Xcaret (34947), Trivago (105931), Kiwi, Sirenis (109948),
Expedia MX (117689), Hoteles.com MX (117687)
+ Mercado Libre via GitHub Actions
"""
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

from agents.mercadolibre import run as run_mercadolibre
from agents.moda         import run_nike, run_lacoste, run_honor, run_laserpecker, run_smartbuyglasses, run_goldenmaple
from agents.viajes       import run as run_viajes
from agents.xcaret       import run as run_xcaret
from agents.alertas      import revisar_alertas
from agents.base         import SUPABASE_URL, supabase_headers

TIENDAS_FIJAS = [
    "Nike MX", "Lacoste MX", "Honor MX", "LaserPecker",
    "SmartBuyGlasses MX", "Golden Maple",
    "Xcaret", "Trivago", "Kiwi", "Sirenis Hotels",
    "Expedia MX", "Hoteles.com MX",
]

def limpiar_tiendas_fijas(ofertas):
    hdrs = supabase_headers()
    fuentes = set(o["fuente"] for o in ofertas if o["fuente"] in TIENDAS_FIJAS)
    for fuente in fuentes:
        try:
            requests.delete(
                f"{SUPABASE_URL}/rest/v1/ofertas?fuente=eq.{requests.utils.quote(fuente)}",
                headers={**hdrs, "Prefer": "return=minimal"}, timeout=10
            )
            print(f"[Supabase] Limpieza: {fuente}")
        except Exception as e:
            print(f"[Supabase] Error limpiando {fuente}: {e}")

def marcar_inactivas_viejas():
    hdrs = supabase_headers()
    for tienda in TIENDAS_FIJAS + ["Mercado Libre"]:
        try:
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/ofertas"
                f"?fuente=eq.{requests.utils.quote(tienda)}&activa=eq.true&select=id,fecha",
                headers=hdrs, timeout=10
            )
            for item in r.json():
                try:
                    if datetime.now() - datetime.strptime(item["fecha"], "%d/%m/%Y %H:%M") > timedelta(days=7):
                        requests.patch(
                            f"{SUPABASE_URL}/rest/v1/ofertas?id=eq.{item['id']}",
                            headers={**hdrs, "Prefer": "return=minimal"},
                            json={"activa": False}, timeout=10
                        )
                except:
                    pass
        except Exception as e:
            print(f"[Supabase] Error limpieza {tienda}: {e}")
    print("[Supabase] Ofertas viejas marcadas inactivas")

def guardar_en_supabase(ofertas):
    hdrs = {**supabase_headers(), "Prefer": "return=minimal"}
    limpiar_tiendas_fijas(ofertas)
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
            print(f"[Supabase] Error guardando: {e}")
    print(f"[Supabase] {nuevas} ofertas guardadas de {len(ofertas)}")

def monitorear():
    print("=" * 55)
    print(f"DEAL TRAVEL — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 55)

    marcar_inactivas_viejas()

    todas = []
    todas.extend(run_mercadolibre())
    todas.extend(run_nike())
    todas.extend(run_lacoste())
    todas.extend(run_honor())
    todas.extend(run_laserpecker())
    todas.extend(run_smartbuyglasses())
    todas.extend(run_goldenmaple())
    todas.extend(run_viajes())
    todas.extend(run_xcaret())

    print(f"\nTOTAL: {len(todas)} ofertas")
    guardar_en_supabase(todas)
    revisar_alertas(todas)

    print("=" * 55)
    print("DONE")
    print("=" * 55)

if __name__ == "__main__":
    monitorear()
