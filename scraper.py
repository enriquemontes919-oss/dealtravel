import os, time, re, schedule, requests
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

EMAIL_DESTINO  = os.getenv("EMAIL_DESTINO", "enrique.montes919@gmail.com")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SUPABASE_URL   = "https://zutcsoloxabwtrvfzmlm.supabase.co"
SUPABASE_KEY   = "sb_publishable_5TNTtixQcRsdbS_kmojIOA_6TNjtiLT"
PRECIO_MAX_MXN = 50000

TIENDAS = [
    {"nombre":"Amazon MX","tipo":"electronico","url":"https://www.amazon.com.mx/deals","espera":6000,"link":"https://www.amazon.com.mx/deals"},
    {"nombre":"Liverpool","tipo":"moda","url":"https://www.liverpool.com.mx/tienda/ofertas","espera":6000,"link":"https://www.liverpool.com.mx/tienda/ofertas"},
    {"nombre":"Walmart MX","tipo":"hogar","url":"https://www.walmart.com.mx/ofertas","espera":6000,"link":"https://www.walmart.com.mx/ofertas"},
    {"nombre":"Mercado Libre","tipo":"electronico","url":"https://www.mercadolibre.com.mx/ofertas","espera":6000,"link":"https://www.mercadolibre.com.mx/ofertas"},
    {"nombre":"Best Buy MX","tipo":"electronico","url":"https://www.bestbuy.com.mx/ofertas","espera":6000,"link":"https://www.bestbuy.com.mx/ofertas"},
    {"nombre":"Coppel","tipo":"hogar","url":"https://www.coppel.com/ofertas","espera":5000,"link":"https://www.coppel.com/ofertas"},
    {"nombre":"Elektra","tipo":"electronico","url":"https://www.elektra.com.mx/ofertas","espera":5000,"link":"https://www.elektra.com.mx/ofertas"},
]

PALABRAS_PROMO = [
    "descuento","descuentos","promocion","promociones","oferta","ofertas",
    "promo","sale","deal","rebaja","ahorro","liquidacion","clearance",
    "meses sin intereses","msi","sin intereses","precio especial",
    "hot sale","buen fin","cyber","black friday","flash",
    "gratis","envio gratis","2x1","precio de socio","oferta del dia",
]

CATEGORIAS_KEYWORDS = {
    "electronico": ["celular","iphone","samsung","laptop","computadora","tablet","tv","television","audifonos","smartwatch","nintendo","playstation","xbox","camara"],
    "moda": ["ropa","zapatos","tenis","vestido","camisa","pantalon","bolsa","cartera","nike","adidas","zara"],
    "hogar": ["sofa","cama","colchon","sala","comedor","cocina","refrigerador","lavadora","microondas","licuadora","mueble"],
    "deporte": ["pesas","bicicleta","yoga","running","gym","proteina"],
    "belleza": ["perfume","crema","maquillaje","shampoo","serum","labial"],
    "juguetes": ["juguete","lego","barbie","hot wheels","muneca","peluche"],
}

def detectar_categoria(texto):
    texto_lower = texto.lower()
    for cat, keywords in CATEGORIAS_KEYWORDS.items():
        if any(kw in texto_lower for kw in keywords):
            return cat
    return "general"

def analizar_promo(texto):
    txt = texto.lower()
    return [p for p in PALABRAS_PROMO if p in txt]

def extraer_ofertas(texto, tienda):
    ofertas = []
    patron = r"\$\s*(\d{1,3}(?:,\d{3})*|\d{4,6})(?:\.\d{2})?"
    precios = []
    for m in re.findall(patron, texto):
        try:
            n = float(m.replace(",", ""))
            if 100 <= n <= PRECIO_MAX_MXN:
                precios.append(n)
        except:
            pass
    precios = sorted(list(set(precios)))
    palabras = analizar_promo(texto)
    categoria = detectar_categoria(texto)
    lineas = [l.strip() for l in texto.split("\n") if 5 < len(l.strip()) < 100]
    productos = [l for l in lineas if any(kw in l.lower() for cat in CATEGORIAS_KEYWORDS.values() for kw in cat)]
    tipo_promo = "Oferta especial"
    if any(p in palabras for p in ["meses sin intereses", "msi"]):
        tipo_promo = "Meses sin intereses"
    elif "liquidacion" in palabras:
        tipo_promo = "Liquidacion"
    elif "hot sale" in palabras:
        tipo_promo = "Hot Sale"
    elif "buen fin" in palabras:
        tipo_promo = "Buen Fin"
    elif "envio gratis" in palabras:
        tipo_promo = "Envio gratis"
    for i, precio in enumerate(precios[:6]):
        producto = productos[i] if i < len(productos) else f"Producto en {tienda['nombre']}"
        ofertas.append({
            "fuente": tienda["nombre"],
            "tipo": categoria,
            "destino": producto[:80],
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "url": tienda["link"],
            "tipo_promo": tipo_promo,
            "palabras_clave": ", ".join(palabras[:4]),
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    return ofertas

def scrape_tienda(page, tienda):
    ofertas = []
    try:
        print(f"[{tienda['nombre']}] Abriendo...")
        try:
            page.goto(tienda["url"], timeout=45000, wait_until="domcontentloaded")
        except:
            try:
                page.goto(tienda["url"], timeout=45000, wait_until="load")
            except Exception as e:
                print(f"  ERROR: {str(e)[:60]}")
                return []
        page.wait_for_timeout(tienda["espera"])
        page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        page.wait_for_timeout(2000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        texto = page.evaluate("() => document.body.innerText")
        if not texto or len(texto) < 100:
            print(f"  AVISO: Pagina vacia")
            return []
        ofertas = extraer_ofertas(texto, tienda)
        print(f"  OK: {len(ofertas)} ofertas")
        for o in ofertas[:3]:
            print(f"    -> {o['destino'][:50]}: {o['precio_fmt']} [{o['tipo_promo']}]")
    except Exception as e:
        print(f"  ERROR: {str(e)[:80]}")
    return ofertas

def guardar_en_supabase(ofertas):
    headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "return=minimal"
    }
    TIENDAS_SCRAPER = ["Amazon MX","Liverpool","Walmart MX","Mercado Libre","Best Buy MX","Coppel","Elektra"]
    for tienda in TIENDAS_SCRAPER:
        try:
            tienda_encoded = tienda.replace(" ", "%20")
            requests.delete(f"{SUPABASE_URL}/rest/v1/ofertas?activa=eq.true&fuente=eq.{tienda_encoded}", headers=headers)
        except:
            pass
    if ofertas:
        try:
            r = requests.post(f"{SUPABASE_URL}/rest/v1/ofertas", headers=headers, json=ofertas)
            if r.status_code in [200, 201]:
                print(f"[Supabase] {len(ofertas)} ofertas guardadas!")
            else:
                print(f"[Supabase] Error: {r.text[:200]}")
        except Exception as e:
            print(f"[Supabase] Error: {e}")

def revisar_alertas(ofertas):
    if not RESEND_API_KEY:
        return
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        r = requests.get(f"{SUPABASE_URL}/rest/v1/alertas?activa=eq.true&select=*", headers=headers)
        alertas = r.json()
        print(f"[Alertas] {len(alertas)} alertas activas")
        r2 = requests.get(f"{SUPABASE_URL}/rest/v1/ofertas?activa=eq.true&select=*", headers=headers)
        todas_ofertas = r2.json()
        print(f"[Ofertas] {len(todas_ofertas)} ofertas en Supabase")
        for alerta in alertas:
            producto_alerta = alerta.get("destino", "").lower()
            palabras_alerta = [w for w in producto_alerta.split() if len(w) > 2]
            for oferta in todas_ofertas:
                producto_oferta = oferta["destino"].lower()
                precio_ok = oferta["precio"] <= float(alerta.get("presupuesto") or 99999)
                tienda_ok = not alerta.get("fuente") or alerta.get("fuente","") == "Cualquier tienda" or alerta.get("fuente","").lower() in oferta["fuente"].lower()
                producto_match = any(word in producto_oferta for word in palabras_alerta)
                if precio_ok and tienda_ok and producto_match:
                    print(f"[Match] {alerta['email']} -> {oferta['destino']}")
                    enviar_alerta_email(alerta, oferta)
                    break
    except Exception as e:
        print(f"[Alertas] Error: {e}")

def enviar_alerta_email(alerta, oferta):
    html = f"""<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <div style="background:#0a1628;padding:20px;border-radius:8px 8px 0 0;">
            <h1 style="color:#38bdf8;margin:0;">Deal<span style="color:#fff;">Travel</span></h1>
            <p style="color:rgba(255,255,255,0.6);margin:5px 0 0;font-size:13px;">Encontramos una oferta para ti</p>
        </div>
        <div style="background:#f8fafc;padding:24px;border-radius:0 0 8px 8px;">
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px;margin-bottom:20px;">
                <p style="margin:0 0 8px;color:#64748b;font-size:13px;">PRODUCTO</p>
                <p style="margin:0 0 16px;font-weight:600;font-size:16px;">{oferta['destino']}</p>
                <p style="margin:0 0 4px;color:#64748b;font-size:13px;">PRECIO</p>
                <p style="margin:0 0 16px;font-size:28px;font-weight:800;color:#0ea5e9;">{oferta['precio_fmt']}</p>
                <p style="margin:0 0 4px;color:#64748b;font-size:13px;">TIENDA</p>
                <p style="margin:0 0 16px;font-weight:600;">{oferta['fuente']}</p>
                <p style="margin:0 0 4px;color:#64748b;font-size:13px;">TIPO</p>
                <p style="margin:0;">{oferta['tipo_promo']}</p>
            </div>
            <a href="{oferta['url']}" style="display:block;background:#38bdf8;color:#0a1628;padding:14px;border-radius:10px;text-decoration:none;font-weight:700;text-align:center;">Ver oferta ahora</a>
            <p style="color:#94a3b8;font-size:11px;margin-top:20px;text-align:center;">Deal Travel · dealtravel.mx</p>
        </div>
    </div>"""
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={
                "from": "Deal Travel <alertas@dealtravel.mx>",
                "to": [alerta["email"]],
                "subject": f"Oferta: {oferta['destino'][:50]} - {oferta['precio_fmt']}",
                "html": html
            }
        )
        if r.status_code == 200:
            print(f"[Email] Enviado a {alerta['email']}")
        else:
            print(f"[Email] Error: {r.status_code}")
    except Exception as e:
        print(f"[Email] Error: {e}")

def monitorear():
    print("=" * 55)
    print(f"DEAL TRAVEL RETAIL - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"Monitoreando {len(TIENDAS)} tiendas")
    print("=" * 55)
    todas = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="es-MX",
            timezone_id="America/Mexico_City"
        )
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page = ctx.new_page()
        for tienda in TIENDAS:
            res = scrape_tienda(page, tienda)
            todas.extend(res)
            time.sleep(3)
        browser.close()
    vistos = set()
    unicas = []
    for o in todas:
        k = f"{o['destino'][:30]}-{o['precio']}"
        if k not in vistos:
            vistos.add(k)
            unicas.append(o)
    print(f"TOTAL: {len(unicas)} ofertas unicas")
    guardar_en_supabase(unicas)
    revisar_alertas(unicas)
    return unicas

if __name__ == "__main__":
    print("Deal Travel Retail Scraper")
    monitorear()
    schedule.every(1).hours.do(monitorear)
    schedule.every().day.at("07:00").do(monitorear)
    schedule.every().day.at("13:00").do(monitorear)
    schedule.every().day.at("19:00").do(monitorear)
    print("Monitoreo activo. Ctrl+C para detener.")
    while True:
        schedule.run_pending()
        time.sleep(60)
