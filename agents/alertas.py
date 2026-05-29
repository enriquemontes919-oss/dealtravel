"""
agents/alertas.py — Sistema de alertas: matching, email consolidado y WhatsApp

FIX Mayo 2026 — Ofertas repetidas en emails:
  Problema raíz: clave_oferta() usaba destino|fuente. Como limpiar_tiendas_fijas()
  borra y re-inserta cada hora con nuevos IDs, las claves seguían siendo iguales
  PERO el campo `ofertas_notificadas` se comparaba contra claves que podían variar
  si el nombre del destino tenía espacios o mayúsculas distintas.

  Solución: clave normalizada = fuente|destino_slug (lowercase, sin espacios extras).
  Además: el matching ahora usa `todas_ofertas` (lo que encontró el scraper en esta
  ejecución) en lugar de releer Supabase, evitando race conditions.
"""
import requests
from datetime import datetime
from agents.base import SUPABASE_URL, RESEND_API_KEY, supabase_headers


def _clave_normalizada(oferta):
    """
    Clave estable: fuente + destino normalizado.
    Resiste re-inserciones con nuevos IDs en Supabase.
    """
    fuente  = (oferta.get("fuente") or "").strip().lower()
    destino = (oferta.get("destino") or "").strip().lower()
    # Quitar prefijo "fuente — " si existe (ej: "Liverpool — Smart TV...")
    if " — " in destino:
        destino = destino.split(" — ", 1)[1]
    return f"{fuente}|{destino[:60]}"


def revisar_alertas(todas_ofertas):
    if not RESEND_API_KEY:
        print("[Alertas] Sin RESEND_API_KEY — emails desactivados")
        return

    if not todas_ofertas:
        print("[Alertas] Sin ofertas para revisar")
        return

    try:
        hdrs  = supabase_headers()
        r     = requests.get(
            f"{SUPABASE_URL}/rest/v1/alertas?activa=eq.true&select=*",
            headers=hdrs, timeout=10
        )
        alertas = r.json()
        print(f"[Alertas] {len(alertas)} alertas activas | {len(todas_ofertas)} ofertas disponibles")

        ahora = datetime.now()

        for alerta in alertas:
            try:
                # ── 1. Verificar expiración ───────────────────────────────
                dias_alerta = alerta.get("dias_alerta") or 7
                fecha_creacion = datetime.fromisoformat(
                    alerta["created_at"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
                dias_transcurridos = (ahora - fecha_creacion).days

                if dias_transcurridos >= dias_alerta:
                    requests.patch(
                        f"{SUPABASE_URL}/rest/v1/alertas?id=eq.{alerta['id']}",
                        headers={**hdrs, "Prefer": "return=minimal"},
                        json={"activa": False}, timeout=10
                    )
                    print(f"[Alertas] Alerta {alerta['id']} expirada — desactivada")
                    continue

                # ── 2. Cooldown 24h ───────────────────────────────────────
                ultimo_envio = alerta.get("ultimo_envio")
                if ultimo_envio:
                    try:
                        ultimo = datetime.fromisoformat(
                            ultimo_envio.replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                        horas = (ahora - ultimo).total_seconds() / 3600
                        if horas < 24:
                            print(f"[Alertas] {alerta['id']} — cooldown ({horas:.1f}h)")
                            continue
                    except Exception:
                        pass

                # ── 3. Claves ya notificadas (normalizadas) ───────────────
                ya_notificados = set(alerta.get("ofertas_notificadas") or [])

                # ── 4. Matching ───────────────────────────────────────────
                producto_alerta = alerta.get("destino", "").lower()
                palabras_alerta = [w for w in producto_alerta.split() if len(w) > 2]
                presupuesto     = float(alerta.get("presupuesto") or 99999)
                fuente_alerta   = alerta.get("fuente", "Cualquier tienda")

                matches_nuevos = []
                for oferta in todas_ofertas:
                    clave = _clave_normalizada(oferta)

                    # Saltar si ya fue notificada
                    if clave in ya_notificados:
                        continue

                    precio_ok = oferta["precio"] == 0 or oferta["precio"] <= presupuesto
                    tienda_ok = (
                        not fuente_alerta
                        or fuente_alerta == "Cualquier tienda"
                        or fuente_alerta.lower() in oferta["fuente"].lower()
                    )
                    producto_ok = any(
                        word in oferta.get("destino", "").lower()
                        or word in oferta.get("palabras_clave", "").lower()
                        for word in palabras_alerta
                    )

                    if precio_ok and tienda_ok and producto_ok:
                        matches_nuevos.append(oferta)

                if not matches_nuevos:
                    print(f"[Alertas] {alerta['id']} ({alerta['email']}) — sin ofertas nuevas")
                    continue

                print(f"[Match] {alerta['email']} → {len(matches_nuevos)} ofertas nuevas")

                # ── 5. Enviar email ───────────────────────────────────────
                enviar_email_consolidado(alerta, matches_nuevos, dias_alerta, dias_transcurridos)

                # ── 6. WhatsApp si eligió ese método ─────────────────────
                telefono = alerta.get("telefono", "").strip()
                if telefono and "whatsapp" in (alerta.get("tipo") or "").lower():
                    enviar_whatsapp(alerta, matches_nuevos)

                # ── 7. Persistir claves notificadas ───────────────────────
                # Guardamos claves normalizadas para que sean estables
                # entre ejecuciones aunque Supabase re-inserte con nuevos IDs
                nuevas_claves = list(ya_notificados) + [
                    _clave_normalizada(o) for o in matches_nuevos
                ]
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/alertas?id=eq.{alerta['id']}",
                    headers={**hdrs, "Prefer": "return=minimal"},
                    json={
                        "ultimo_envio":        ahora.isoformat(),
                        "ofertas_notificadas": nuevas_claves,
                    },
                    timeout=10
                )

            except Exception as e:
                print(f"[Alertas] Error alerta {alerta.get('id')}: {e}")

    except Exception as e:
        print(f"[Alertas] Error general: {e}")


# ── Utilidades ────────────────────────────────────────────────────────────────

def _limpiar_numero(telefono):
    numero = "".join(filter(str.isdigit, telefono))
    if not numero.startswith("52") and len(numero) == 10:
        numero = "52" + numero
    return numero


def enviar_whatsapp(alerta, ofertas):
    telefono = alerta.get("telefono", "").strip()
    if not telefono:
        return
    numero = _limpiar_numero(telefono)
    lineas = [f"🔔 *Deal Travel* — Nueva oferta para '{alerta['destino']}':\n"]
    for o in ofertas[:3]:
        precio_txt = o["precio_fmt"]
        lineas += [
            f"• *{o['destino'][:40]}*",
            f"  {o['fuente']} · {precio_txt}",
            f"  {o['url']}\n",
        ]
    lineas.append("Ver todas: https://www.dealtravel.mx")
    mensaje = "\n".join(lineas)
    link = f"https://wa.me/{numero}?text={requests.utils.quote(mensaje)}"
    print(f"[WhatsApp] Link generado para {numero}")
    return link


def enviar_email_consolidado(alerta, ofertas, dias_alerta, dias_transcurridos):
    dias_restantes = dias_alerta - dias_transcurridos

    # Sección WhatsApp
    telefono  = alerta.get("telefono", "").strip()
    wa_section = ""
    if telefono:
        numero = _limpiar_numero(telefono)
        lineas_wa = [f"🔔 Deal Travel — Oferta para '{alerta['destino']}':\n"]
        for o in ofertas[:3]:
            lineas_wa.append(
                f"• {o['destino'][:40]} — {o['fuente']} · {o['precio_fmt']} — {o['url']}"
            )
        lineas_wa.append("\nVer todas: https://www.dealtravel.mx")
        wa_link = f"https://wa.me/{numero}?text={requests.utils.quote(chr(10).join(lineas_wa))}"
        wa_section = f"""
        <div style="text-align:center;margin-top:12px;">
            <a href="{wa_link}" style="display:inline-flex;align-items:center;gap:6px;background:#25D366;color:#fff;padding:8px 18px;border-radius:980px;text-decoration:none;font-size:0.8rem;font-weight:600;">
                💬 Ver ofertas en WhatsApp
            </a>
        </div>"""

    # Cards de ofertas
    ofertas_html = ""
    for oferta in ofertas[:8]:
        precio_orig      = oferta.get("precio_original")
        descuento        = oferta.get("descuento_pct")
        precio_orig_html = ""
        if precio_orig and precio_orig > oferta["precio"]:
            precio_orig_html = (
                f'<span style="text-decoration:line-through;color:#aeaeb2;'
                f'font-size:0.8rem;">${precio_orig:,.0f}</span> '
            )
        descuento_badge = (
            f'<span style="background:#ff3b30;color:#fff;font-size:0.65rem;'
            f'font-weight:700;padding:2px 7px;border-radius:6px;margin-left:6px;">'
            f'-{descuento}%</span>'
            if descuento else ""
        )
        precio_display = (
            f'<span style="font-size:1.4rem;font-weight:800;color:#0ea5e9;">'
            f'{oferta["precio_fmt"]}</span>'
        )
        ofertas_html += f"""
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div style="flex:1;">
                    <p style="margin:0 0 4px;font-size:0.7rem;color:#0071e3;font-weight:600;text-transform:uppercase;">{oferta['fuente']}</p>
                    <p style="margin:0 0 8px;font-weight:600;font-size:0.95rem;color:#1d1d1f;">{oferta['destino']}</p>
                    <p style="margin:0;font-size:0.75rem;color:#64748b;">{oferta['tipo_promo']}</p>
                </div>
                <div style="text-align:right;">
                    <p style="margin:0 0 4px;">{precio_orig_html}{precio_display}{descuento_badge}</p>
                    <a href="{oferta['url']}" style="background:#0071e3;color:#fff;padding:6px 14px;border-radius:980px;text-decoration:none;font-size:0.78rem;font-weight:600;">Ver →</a>
                </div>
            </div>
        </div>"""

    html = f"""<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px;margin:0 auto;background:#f8fafc;">
        <div style="background:#0a1628;padding:24px;border-radius:12px 12px 0 0;text-align:center;">
            <h1 style="color:#38bdf8;margin:0 0 4px;font-size:1.8rem;">Deal<span style="color:#fff;">Travel</span></h1>
            <p style="color:rgba(255,255,255,0.6);margin:0;font-size:0.85rem;">Encontramos {len(ofertas)} oferta{'s' if len(ofertas)>1 else ''} nuevas para ti</p>
        </div>
        <div style="background:#fff;padding:24px;border-radius:0 0 12px 12px;">
            <div style="background:#f0f8ff;border:1px solid #cce5ff;border-radius:10px;padding:12px 16px;margin-bottom:20px;">
                <p style="margin:0;font-size:0.85rem;color:#0071e3;">
                    🔔 Tu alerta: <strong>{alerta['destino']}</strong> ·
                    Presupuesto: <strong>${float(alerta.get('presupuesto',0)):,.0f} MXN</strong> ·
                    <span style="color:#64748b;">Vence en {dias_restantes} día{'s' if dias_restantes!=1 else ''}</span>
                </p>
            </div>
            {ofertas_html}
            <div style="text-align:center;margin-top:20px;padding-top:16px;border-top:1px solid #e2e8f0;">
                <a href="https://www.dealtravel.mx" style="background:#0071e3;color:#fff;padding:12px 24px;border-radius:980px;text-decoration:none;font-weight:600;font-size:0.9rem;">Ver todas las ofertas en dealtravel.mx</a>
            </div>
            {wa_section}
            <p style="color:#94a3b8;font-size:0.72rem;margin-top:16px;text-align:center;">
                Deal Travel · dealtravel.mx<br>
                Tu alerta expira en {dias_restantes} día{'s' if dias_restantes!=1 else ''}.
                <a href="https://www.dealtravel.mx#alerta" style="color:#0071e3;">Renovar alerta</a>
            </p>
        </div>
    </div>"""

    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from":    "Deal Travel <alertas@dealtravel.mx>",
                "to":      [alerta["email"]],
                "subject": (
                    f"🔥 {len(ofertas)} oferta{'s' if len(ofertas)>1 else ''}"
                    f" nueva{'s' if len(ofertas)>1 else ''}"
                    f" para '{alerta['destino']}' — dealtravel.mx"
                ),
                "html": html,
            },
            timeout=15
        )
        if r.status_code == 200:
            print(f"[Email] ✓ Enviado a {alerta['email']} ({len(ofertas)} ofertas)")
        else:
            print(f"[Email] Error {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"[Email] Excepción: {e}")
