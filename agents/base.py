"""
agents/base.py — Utilidades compartidas por todos los agentes
"""
import os
import requests
from datetime import datetime, timedelta

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://zutcsoloxabwtrvfzmlm.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_5TNTtixQcRsdbS_kmojIOA_6TNjtiLT")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
AWIN_ID    = "2876425"
AMAZON_TAG = "dealtravelmx-20"
EXPEDIA_LINK = "https://www.awin1.com/cread.php?awinmid=117689&awinaffid=2876425&ued=https%3A%2F%2Fwww.expedia.mx%2FHotels"
HOTELES_LINK = "https://www.awin1.com/cread.php?awinmid=117687&awinaffid=2876425&ued=https%3A%2F%2Fwww.hoteles.com"
PRECIO_MAX_MXN = 50000

MESES_ES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

def ahora_str():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

def precio_original(precio, descuento_pct):
    return round(precio / (1 - descuento_pct / 100))

def amazon_url(asin):
    return f"https://www.amazon.com.mx/dp/{asin}?tag={AMAZON_TAG}"

def generar_fechas_viaje(indice):
    hoy = datetime.now()
    dias_hasta_viernes = (4 - hoy.weekday()) % 7
    if dias_hasta_viernes == 0:
        dias_hasta_viernes = 7
    viernes = hoy + timedelta(days=dias_hasta_viernes)
    domingo = viernes + timedelta(days=2)
    en_2_semanas = hoy + timedelta(days=14)
    en_3_semanas = hoy + timedelta(days=21)
    en_1_mes    = hoy + timedelta(days=30)
    en_5_semanas = hoy + timedelta(days=37)
    def fmt(d):
        return f"{d.day} {MESES_ES[d.month - 1]}"
    rangos = [
        f"{fmt(viernes)} – {fmt(domingo)}",
        f"{fmt(en_2_semanas)} – {fmt(en_3_semanas)}",
        f"{fmt(en_1_mes)} – {fmt(en_5_semanas)}",
    ]
    return rangos[indice % 3]

def supabase_headers():
    return {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

def clave_oferta(oferta):
    return f"{oferta.get('destino','')[:50]}|{oferta.get('fuente','')}"

