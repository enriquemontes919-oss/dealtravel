"""
agents/alertas.py — Sistema de alertas

FIXES Sep 2026:
- Cooldown mínimo 6h (no 24h) para alertas nuevas, pero nunca repetir misma oferta
- Clave normalizada más estable — solo fuente + primeras palabras del destino
- URLs directas en el email (landing de la oferta, no homepage)
- Matching más amplio para viajes (palabras clave de destino)
"""
import requests
from datetime import datetime
from agents.base import SUPABASE_URL, RESEND_API_KEY, supabase_headers


def _clave_normalizada(oferta):
    """
    Clave estable basada en fuente + destino sin fechas ni precios.
    Resiste re-inserciones horarias con nuevos IDs.
    """
    fuente  = (oferta.get("fuente") or "").strip().lower()
    destino = (oferta.get("destino") or "").strip().lower()
    # Quitar prefijo "fuente — "
    if " — " in destino:
        destino = destino.split(" — ", 1)[1]
    # Quitar fechas dinámicas tipo "· 4 Sep – 6 Sep"
    if " · " in destino:
        destino = destino.split(" · ")[0]
    # Solo primeras 40 chars para estabilidad
    return f"{fuente}|{destino[:40].strip()}"


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

                # ── 2. Cooldown mínimo 6h entre emails ───────────────────
                ultimo_envio = alerta.get("ultimo_envio")
                if ultimo_envio:
                    try:
                        ultimo = datetime.fromisoformat(
                            ultimo_envio.replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                        horas = (ahora - ultimo).total_seconds() / 3600
                        if horas < 6:
                            print(f"[Alertas] {alerta['id']} — cooldown ({horas:.1f}h)")
                            continue
                    except Exception:
                        pass

                # ── 3. Claves ya notificadas ──────────────────────────────
                ya_notificados = set(alerta.get("ofertas_notificadas") or [])

                # ── 4. Matching ───────────────────────────────────────────
                producto_alerta = (alerta.get("destino") or "").lower()
                # Palabras de búsqueda — incluir variantes de destino
                palabras_alerta = [w for w in producto_alerta.split() if len(w) > 2]
                presupuesto     = float(alerta.get("presupuesto") or 99999)
                fuente_alerta   = alerta.get("fuente") or "Cualquier tienda"

                matches_nuevos = []
                for oferta in todas_ofertas:
                    clave = _clave_normalizada(oferta)

                    # Skip si ya fue notificada
                    if clave in ya_notificados:
                        continue

                    precio_ok = oferta.get("precio", 0) == 0 or oferta.get("precio", 0) <= presupuesto

                    tienda_ok = (
                        not fuente_alerta
                        or fuente_alerta == "Cualquier tienda"
                        or fuente_alerta.lower() in (oferta.get("fuente") or "").lower()
                    )

                    destino_oferta   = (oferta.get("destino") or "").lower()
                    keywords_oferta  = (oferta.get("palabras_clave") or "").lower()
                    texto_oferta     = f"{destino_oferta} {keywords_oferta}"

                    producto_ok = any(
                        word in texto_oferta
                        for word in palabras_alerta
                    )

                    if precio_ok and tienda_ok and producto_ok:
                        matches_nuevos.append(oferta)

                if not matches_nuevos:
                    print(f"[Alertas] {alerta['id']} ({alerta.get('email')}) — sin ofertas nuevas")
                    continue

                print(f"[Match] {alerta.get('email')} → {len(matches_nuevos)} ofertas nuevas")

                # ── 5. Enviar email ───────────────────────────────────────
                enviar_email_consolidado(alerta, matches_nuevos, dias_alerta, dias_transcurridos)

                # ── 6. WhatsApp ───────────────────────────────────────────
                telefono = (alerta.get("telefono") or "").strip()
                if telefono and "whatsapp" in (alerta.get("tipo") or "").lower():
                    enviar_whatsapp(alerta, matches_nuevos)

                # ── 7. Persistir claves + timestamp ───────────────────────
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
                print(f"[Alertas] {alerta['id']} — claves guardadas ({len(nuevas_claves)} total)")

            except Exception as e:
                print(f"[Alertas] Error alerta {alerta.get('id')}: {e}")

    except Exception as e:
        print(f"[Alertas] Error general: {e}")


def _limpiar_numero(telefono):
    numero = "".join(filter(str.isdigit, telefono))
    if not numero.startswith("52") and len(numero) == 10:
        numero = "52" + numero
    return numero


def enviar_whatsapp(alerta, ofertas):
    telefono = (alerta.get("telefono") or "").strip()
    if not telefono:
        return
    numero = _limpiar_numero(telefono)
    lineas = [f"dealtravel.mx — Nueva oferta para '{alerta.get('destino')}':\n"]
    for o in ofertas[:3]:
        lineas += [
            f"• {o.get('destino','')[:40]}",
            f"  {o.get('fuente','')} · {o.get('precio_fmt','')}",
            f"  {o.get('url','')}\n",
        ]
    lineas.append("Ver todas: https://www.dealtravel.mx")
    mensaje = "\n".join(lineas)
    link = f"https://wa.me/{numero}?text={requests.utils.quote(mensaje)}"
    print(f"[WhatsApp] Link generado para {numero}")
    return link


def enviar_email_consolidado(alerta, ofertas, dias_alerta, dias_transcurridos):
    dias_restantes = max(0, dias_alerta - dias_transcurridos)

    # WhatsApp section
    telefono = (alerta.get("telefono") or "").strip()
    wa_section = ""
    if telefono:
        numero = _limpiar_numero(telefono)
        lineas_wa = [f"dealtravel.mx — Oferta para '{alerta.get('destino')}':\n"]
        for o in ofertas[:3]:
            lineas_wa.append(
                f"• {o.get('destino','')[:40]} — {o.get('fuente','')} · {o.get('precio_fmt','')} — {o.get('url','')}"
            )
        lineas_wa.append("\nVer todas: https://www.dealtravel.mx")
        wa_link = f"https://wa.me/{numero}?text={requests.utils.quote(chr(10).join(lineas_wa))}"
        wa_section = f"""
        <div style="text-align:center;margin-top:12px;">
            <a href="{wa_link}" style="display:inline-flex;align-items:center;gap:6px;background:#25D366;color:#fff;padding:8px 18px;border-radius:980px;text-decoration:none;font-size:0.8rem;font-weight:600;">
                Ver en WhatsApp
            </a>
        </div>"""

    # Cards de ofertas con URL directa
    ofertas_html = ""
    for oferta in ofertas[:8]:
        precio_orig  = oferta.get("precio_original")
        descuento    = oferta.get("descuento_pct")
        precio       = oferta.get("precio", 0)
        precio_fmt   = oferta.get("precio_fmt", "Ver oferta")
        url_oferta   = oferta.get("url", "https://www.dealtravel.mx")

        precio_orig_html = ""
        if precio_orig and precio_orig > precio and precio > 0:
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

        ofertas_html += f"""
        <div style="background:#fff;border:1px solid #ede9ff;border-radius:12px;padding:16px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div style="flex:1;">
                    <p style="margin:0 0 4px;font-size:0.68rem;color:#5200FF;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">{oferta.get('fuente','')}</p>
                    <p style="margin:0 0 6px;font-weight:600;font-size:0.95rem;color:#1d1d1f;line-height:1.3;">{oferta.get('destino','')}</p>
                    <p style="margin:0;font-size:0.72rem;color:#64748b;">{oferta.get('tipo_promo','')}</p>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <p style="margin:0 0 8px;">{precio_orig_html}<span style="font-size:1.3rem;font-weight:800;color:#5200FF;">{precio_fmt}</span>{descuento_badge}</p>
                    <a href="{url_oferta}" style="background:#5200FF;color:#fff;padding:7px 16px;border-radius:980px;text-decoration:none;font-size:0.78rem;font-weight:700;">Ver oferta →</a>
                </div>
            </div>
        </div>"""

    html = f"""<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px;margin:0 auto;background:#f7f6ff;">
        <div style="background:#5200FF;padding:28px 24px;border-radius:14px 14px 0 0;text-align:center;">
            <div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:6px;letter-spacing:-0.5px;">
                dealtravel<span style="color:#CCFF00;">.mx</span>
            </div>
            <p style="color:rgba(255,255,255,0.75);margin:0;font-size:0.85rem;">
                {len(ofertas)} oferta{'s' if len(ofertas)>1 else ''} nueva{'s' if len(ofertas)>1 else ''} para ti
            </p>
        </div>
        <div style="background:#fff;padding:24px;border-radius:0 0 14px 14px;">
            <div style="background:#f0ebff;border:1px solid rgba(82,0,255,0.15);border-radius:10px;padding:12px 16px;margin-bottom:20px;">
                <p style="margin:0;font-size:0.85rem;color:#5200FF;">
                    Tu alerta: <strong>{alerta.get('destino','')}</strong> ·
                    Presupuesto máx: <strong>${float(alerta.get('presupuesto') or 0):,.0f} MXN</strong> ·
                    <span style="color:#64748b;">Vence en {dias_restantes} día{'s' if dias_restantes!=1 else ''}</span>
                </p>
            </div>
            {ofertas_html}
            <div style="text-align:center;margin-top:20px;padding-top:16px;border-top:1px solid #ede9ff;">
                <a href="https://www.dealtravel.mx" style="background:#5200FF;color:#fff;padding:12px 28px;border-radius:980px;text-decoration:none;font-weight:700;font-size:0.9rem;">Ver todas las ofertas</a>
            </div>
            {wa_section}
            <p style="color:#94a3b8;font-size:0.7rem;margin-top:16px;text-align:center;line-height:1.6;">
                dealtravel.mx · Tu alerta vence en {dias_restantes} día{'s' if dias_restantes!=1 else ''}.<br>
                <a href="https://www.dealtravel.mx#alerta" style="color:#5200FF;text-decoration:none;">Crear nueva alerta</a>
            </p>
        </div>
    </div>"""

    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "from":    "dealtravel.mx <alertas@dealtravel.mx>",
                "to":      [alerta["email"]],
                "subject": (
                    f"{len(ofertas)} oferta{'s' if len(ofertas)>1 else ''} nueva{'s' if len(ofertas)>1 else ''}"
                    f" para '{alerta.get('destino','')}' — dealtravel.mx"
                ),
                "html": html,
            },
            timeout=15
        )
        if r.status_code == 200:
            print(f"[Email] Enviado a {alerta['email']} ({len(ofertas)} ofertas)")
        else:
            print(f"[Email] Error {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"[Email] Excepción: {e}")
