import os, time, re, schedule, requests, hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SUPABASE_URL   = "https://zutcsoloxabwtrvfzmlm.supabase.co"
SUPABASE_KEY   = "sb_publishable_5TNTtixQcRsdbS_kmojIOA_6TNjtiLT"
PRECIO_MAX_MXN = 50000
AWIN_ID        = "2876425"

CATEGORIAS_KEYWORDS = {
    "electronico": ["celular","iphone","samsung","laptop","computadora","tablet","tv","television","audifonos","smartwatch","nintendo","playstation","xbox","camara","apple","macbook","ipad"],
    "moda": ["ropa","zapatos","tenis","vestido","camisa","pantalon","bolsa","cartera","nike","adidas","zara","puma","reebok","vans","converse","lacoste","shein"],
    "hogar": ["sofa","cama","colchon","sala","comedor","cocina","refrigerador","lavadora","microondas","licuadora","mueble","silla","mesa"],
    "deporte": ["pesas","bicicleta","yoga","running","gym","proteina","futbol","tenis","pelota"],
    "belleza": ["perfume","crema","maquillaje","shampoo","serum","labial","skincare"],
    "juguetes": ["juguete","lego","barbie","hot wheels","muneca","peluche"],
    "viajes": ["hotel","vuelo","viaje","hospedaje","resort","vacaciones","aeropuerto"],
}

def detectar_categoria(texto):
    texto_lower = texto.lower()
    for cat, keywords in CATEGORIAS_KEYWORDS.items():
        if any(kw in texto_lower for kw in keywords):
            return cat
    return "general"

def generar_id(destino, precio, fuente):
    """ID único para evitar duplicados"""
    key = f"{destino[:30]}-{precio}-{fuente}"
    return hashlib.md5(key.encode()).hexdigest()[:12]

def oferta_ya_existe(headers_sb, destino, precio, fuente):
    """Verifica si la oferta ya está en Supabase"""
    try:
        destino_encoded = requests.utils.quote(destino[:30])
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/ofertas?destino=ilike.*{destino_encoded[:20]}*&precio=eq.{precio}&fuente=eq.{fuente}",
            headers=headers_sb,
            timeout=10
        )
        data = r.json()
        return len(data) > 0
    except:
        return False

# ─── MERCADO LIBRE ────────────────────────────────────────────────────────────

def scrape_mercadolibre():
    ofertas = []
    categorias = [
        ("MLM1055", "electronico"),
        ("MLM1430", "moda"),
        ("MLM1574", "hogar"),
        ("MLM1276", "deporte"),
        ("MLM1246", "belleza"),
    ]
    for cat_id, tipo in categorias:
        try:
            url = f"https://api.mercadolibre.com/sites/MLM/search?category={cat_id}&sort=price_asc&limit=6"
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                continue
            data = r.json()
            for item in data.get("results", []):
                precio = item.get("price", 0)
                original = item.get("original_price") or precio
                if not (100 <= precio <= PRECIO_MAX_MXN):
                    continue
                if original <= precio:
                    continue
                descuento = round((1 - precio / original) * 100)
                if descuento < 10:
                    continue
                ofertas.append({
                    "fuente": "Mercado Libre",
                    "tipo": tipo,
                    "destino": item["title"][:80],
                    "precio": precio,
                    "precio_fmt": f"${precio:,.0f} MXN",
                    "url": item["permalink"],
                    "tipo_promo": f"-{descuento}% descuento",
                    "palabras_clave": tipo,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "activa": True
                })
        except Exception as e:
            print(f"[MercadoLibre] Error: {e}")
    print(f"[Mercado Libre] {len(ofertas)} ofertas nuevas")
    return ofertas

# ─── AMAZON ───────────────────────────────────────────────────────────────────

def scrape_amazon():
    ofertas = []
    busquedas = [
        ("laptop", "electronico"),
        ("iphone", "electronico"),
        ("samsung tv", "electronico"),
        ("audifonos bluetooth", "electronico"),
        ("cafetera", "hogar"),
        ("nintendo switch", "electronico"),
        ("perfume mujer", "belleza"),
        ("tenis deportivos", "moda"),
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-MX,es;q=0.9",
    }
    for query, tipo in busquedas:
        try:
            url = f"https://www.amazon.com.mx/s?k={query.replace(' ','+')}"
            r = requests.get(url, headers=headers, timeout=15)
            precios = re.findall(r'\$\s*(\d{1,3}(?:,\d{3})*)', r.text)
            titulos = re.findall(r'"name"\s*:\s*"([^"]{10,80})"', r.text)
            if precios and titulos:
                for i, (p, t) in enumerate(zip(precios[:3], titulos[:3])):
                    try:
                        precio = float(p.replace(",", ""))
                        if 500 <= precio <= PRECIO_MAX_MXN:
                            ofertas.append({
                                "fuente": "Amazon MX",
                                "tipo": tipo,
                                "destino": t[:80],
                                "precio": precio,
                                "precio_fmt": f"${precio:,.0f} MXN",
                                "url": f"https://www.amazon.com.mx/s?k={query.replace(' ','+')}",
                                "tipo_promo": "Oferta Amazon",
                                "palabras_clave": query,
                                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "activa": True
                            })
                    except:
                        pass
        except Exception as e:
            print(f"[Amazon] Error {query}: {e}")
    print(f"[Amazon MX] {len(ofertas)} ofertas nuevas")
    return ofertas

# ─── NIKE ─────────────────────────────────────────────────────────────────────

def scrape_nike():
    ofertas = []
    try:
        url = "https://api.nike.com/product_feed/threads/v2/?filter=marketplace(MX)&filter=language(es-419)&filter=employeePrice(true)&anchor=0&count=20"
        r = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        if r.status_code == 200:
            data = r.json()
            for thread in data.get("objects", [])[:10]:
                try:
                    info = thread.get("productInfo", [{}])[0]
                    prices = info.get("merchPrice", {})
                    nombre = thread.get("publishedContent", {}).get("properties", {}).get("title", "")
                    precio = prices.get("currentPrice", 0)
                    original = prices.get("fullPrice", precio)
                    if not nombre or not precio:
                        continue
                    if not (300 <= precio <= PRECIO_MAX_MXN):
                        continue
                    descuento = round((1 - precio / original) * 100) if original > precio else 0
                    ofertas.append({
                        "fuente": "Nike MX",
                        "tipo": "moda",
                        "destino": nombre[:80],
                        "precio": precio,
                        "precio_fmt": f"${precio:,.0f} MXN",
                        "url": "https://www.nike.com/mx/w/sale-3yaep",
                        "tipo_promo": f"-{descuento}% en Nike" if descuento > 0 else "Nike MX",
                        "palabras_clave": "nike, tenis, ropa deportiva",
                        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "activa": True
                    })
                except:
                    pass
    except Exception as e:
        print(f"[Nike] Error: {e}")
    print(f"[Nike MX] {len(ofertas)} ofertas nuevas")
    return ofertas

# ─── ADIDAS ───────────────────────────────────────────────────────────────────

def scrape_adidas():
    ofertas = []
    try:
        url = "https://www.adidas.mx/api/products/search?query=sale&start=0&count=10"
        r = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        if r.status_code == 200:
            data = r.json()
            for item in data.get("products", [])[:6]:
                try:
                    nombre = item.get("name", "")
                    precio = item.get("salePrice", 0) or item.get("price", 0)
                    original = item.get("price", precio)
                    if not nombre or not precio:
                        continue
                    if not (300 <= precio <= PRECIO_MAX_MXN):
                        continue
                    descuento = round((1 - precio / original) * 100) if original > precio else 0
                    ofertas.append({
                        "fuente": "Adidas MX",
                        "tipo": "moda",
                        "destino": nombre[:80],
                        "precio": precio,
                        "precio_fmt": f"${precio:,.0f} MXN",
                        "url": "https://www.adidas.mx/sale",
                        "tipo_promo": f"-{descuento}% Adidas" if descuento > 0 else "Sale Adidas",
                        "palabras_clave": "adidas, tenis, ropa deportiva",
                        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "activa": True
                    })
                except:
                    pass
    except Exception as e:
        print(f"[Adidas] Error: {e}")
    print(f"[Adidas MX] {len(ofertas)} ofertas nuevas")
    return ofertas

# ─── WALMART ──────────────────────────────────────────────────────────────────

def scrape_walmart():
    ofertas = []
    busquedas = [
        ("laptop", "electronico"),
        ("television", "electronico"),
        ("refrigerador", "hogar"),
        ("licuadora", "hogar"),
        ("tenis", "moda"),
        ("videojuegos", "electronico"),
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Accept": "application/json",
    }
    for query, tipo in busquedas:
        try:
            url = f"https://www.walmart.com.mx/api/2/page/namespace/search?query={query}&page=1&pageSize=5"
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                continue
            data = r.json()
            items = data.get("data", {}).get("search", {}).get("products", {}).get("edges", [])
            for edge in items[:4]:
                node = edge.get("node", {})
                precio = node.get("priceInfo", {}).get("currentPrice", {}).get("price", 0)
                original = node.get("priceInfo", {}).get("wasPrice", {}).get("price", precio)
                nombre = node.get("name", "")
                link = node.get("canonicalUrl", "")
                if not nombre or not precio:
                    continue
                if not (300 <= precio <= PRECIO_MAX_MXN):
                    continue
                descuento = round((1 - precio / original) * 100) if original > precio else 0
                if descuento < 5:
                    continue
                ofertas.append({
                    "fuente": "Walmart MX",
                    "tipo": tipo,
                    "destino": nombre[:80],
                    "precio": precio,
                    "precio_fmt": f"${precio:,.0f} MXN",
                    "url": f"https://www.walmart.com.mx{link}" if link else "https://www.walmart.com.mx/ofertas",
                    "tipo_promo": f"-{descuento}% Walmart",
                    "palabras_clave": query,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "activa": True
                })
        except Exception as e:
            print(f"[Walmart] Error {query}: {e}")
    print(f"[Walmart MX] {len(ofertas)} ofertas nuevas")
    return ofertas

# ─── SHEIN ────────────────────────────────────────────────────────────────────

def scrape_shein():
    ofertas = []
    try:
        url = "https://mx.shein.com/api/productList/info/v1?cat_id=1727&limit=10&sort=8&page=1"
        r = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })
        if r.status_code == 200:
            data = r.json()
            for item in data.get("info", {}).get("products", [])[:6]:
                try:
                    nombre = item.get("goods_name", "")
                    precio = float(item.get("salePrice", {}).get("amount", 0))
                    original = float(item.get("retailPrice", {}).get("amount", precio))
                    if not nombre or not precio:
                        continue
                    if not (100 <= precio <= PRECIO_MAX_MXN):
                        continue
                    descuento = round((1 - precio / original) * 100) if original > precio else 0
                    ofertas.append({
                        "fuente": "Shein MX",
                        "tipo": "moda",
                        "destino": nombre[:80],
                        "precio": precio,
                        "precio_fmt": f"${precio:,.0f} MXN",
                        "url": "https://mx.shein.com/promotion/flash-sale.html",
                        "tipo_promo": f"-{descuento}% Shein" if descuento > 0 else "Oferta Shein",
                        "palabras_clave": "shein, moda, ropa",
                        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "activa": True
                    })
                except:
                    pass
    except Exception as e:
        print(f"[Shein] Error: {e}")
    print(f"[Shein MX] {len(ofertas)} ofertas nuevas")
    return ofertas

# ─── ALIEXPRESS ───────────────────────────────────────────────────────────────

def scrape_aliexpress():
    ofertas = []
    try:
        url = "https://gw.aliexpress.com/ajaxapi/v2/search/product?keywords=ofertas&page=1&pageSize=10&currency=MXN&locale=es_MX&country=MX"
        r = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", {}).get("products", [])
            for item in items[:6]:
                try:
                    nombre = item.get("title", "")
                    precio = float(item.get("prices", {}).get("salePrice", {}).get("minPrice", 0))
                    original = float(item.get("prices", {}).get("originalPrice", {}).get("minPrice", precio))
                    if not nombre or not precio:
                        continue
                    if not (100 <= precio <= PRECIO_MAX_MXN):
                        continue
                    descuento = round((1 - precio / original) * 100) if original > precio else 0
                    ofertas.append({
                        "fuente": "AliExpress",
                        "tipo": detectar_categoria(nombre),
                        "destino": nombre[:80],
                        "precio": precio,
                        "precio_fmt": f"${precio:,.0f} MXN",
                        "url": item.get("productDetailUrl", "https://www.aliexpress.com"),
                        "tipo_promo": f"-{descuento}% AliExpress" if descuento > 0 else "Oferta AliExpress",
                        "palabras_clave": "aliexpress, importado",
                        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "activa": True
                    })
                except:
                    pass
    except Exception as e:
        print(f"[AliExpress] Error: {e}")
    print(f"[AliExpress] {len(ofertas)} ofertas nuevas")
    return ofertas

# ─── AWIN — VIAJES ────────────────────────────────────────────────────────────

def scrape_awin_viajes():
    """Genera ofertas de viajes con links afiliados Awin"""
    ofertas = []
    destinos_trivago = [
        ("Cancún, México", 1200, 1800),
        ("Ciudad de México", 800, 1400),
        ("Los Cabos", 1500, 2500),
        ("Puerto Vallarta", 1100, 1900),
        ("Playa del Carmen", 1300, 2100),
    ]
    for destino, precio_min, precio_max in destinos_trivago:
        precio = precio_min
        ofertas.append({
            "fuente": "Trivago",
            "tipo": "viajes",
            "destino": f"Hotel en {destino}",
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN/noche",
            "url": f"https://www.awin1.com/cread.php?s=3330897&v=20563&q=474350&r={AWIN_ID}&ued=https://www.trivago.com.mx/?search/200-{destino.replace(' ','%20')}",
            "tipo_promo": "Precio por noche desde",
            "palabras_clave": "hotel, viaje, hospedaje, trivago",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })

    # Kiwi — vuelos
    vuelos = [
        ("CDMX → Cancún", 1800),
        ("CDMX → Los Cabos", 2100),
        ("CDMX → Guadalajara", 900),
        ("CDMX → Monterrey", 950),
        ("CDMX → Miami", 4500),
    ]
    for ruta, precio in vuelos:
        ofertas.append({
            "fuente": "Kiwi",
            "tipo": "viajes",
            "destino": f"Vuelo {ruta}",
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "url": f"https://www.awin1.com/cread.php?s=2702014&v=20563&q=395852&r={AWIN_ID}",
            "tipo_promo": "Vuelo desde",
            "palabras_clave": "vuelo, avion, kiwi, viaje",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })

    # Sirenis Hotels
    ofertas.append({
        "fuente": "Sirenis Hotels",
        "tipo": "viajes",
        "destino": "Resort Todo Incluido Riviera Maya",
        "precio": 2800,
        "precio_fmt": "$2,800 MXN/noche",
        "url": f"https://www.awin1.com/cread.php?s=SIRENIS&v=20563&q=SIRENIS&r={AWIN_ID}&ued=https://www.sirenishotels.com",
        "tipo_promo": "Todo incluido desde",
        "palabras_clave": "hotel, resort, todo incluido, sirenis",
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "activa": True
    })

    print(f"[Awin Viajes] {len(ofertas)} ofertas")
    return ofertas

# ─── SUPABASE ─────────────────────────────────────────────────────────────────

def marcar_inactivas_viejas():
    """Marca como inactivas ofertas del scraper con más de 7 días"""
    headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    fecha_limite = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y %H:%M")
    TIENDAS_SCRAPER = ["Amazon MX","Mercado Libre","Walmart MX","Nike MX","Adidas MX","Shein MX","AliExpress","Trivago","Kiwi","Sirenis Hotels"]
    try:
        for tienda in TIENDAS_SCRAPER:
            tienda_encoded = requests.utils.quote(tienda)
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/ofertas?fuente=eq.{tienda_encoded}&activa=eq.true&select=id,fecha",
                headers=headers, timeout=10
            )
            items = r.json()
            for item in items:
                try:
                    fecha_oferta = datetime.strptime(item["fecha"], "%d/%m/%Y %H:%M")
                    if datetime.now() - fecha_oferta > timedelta(days=7):
                        requests.patch(
                            f"{SUPABASE_URL}/rest/v1/ofertas?id=eq.{item['id']}",
                            headers={**headers, "Prefer": "return=minimal"},
                            json={"activa": False},
                            timeout=10
                        )
                except:
                    pass
        print("[Supabase] Ofertas viejas marcadas como inactivas")
    except Exception as e:
        print(f"[Supabase] Error limpieza: {e}")

def guardar_en_supabase(ofertas):
    headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "return=minimal"
    }
    nuevas = 0
    for oferta in ofertas:
        try:
            if not oferta_ya_existe(headers, oferta["destino"], oferta["precio"], oferta["fuente"]):
                r = requests.post(
                    f"{SUPABASE_URL}/rest/v1/ofertas",
                    headers=headers,
                    json=oferta,
                    timeout=10
                )
                if r.status_code in [200, 201]:
                    nuevas += 1
        except Exception as e:
            print(f"[Supabase] Error guardando: {e}")
    print(f"[Supabase] {nuevas} ofertas nuevas guardadas (de {len(ofertas)} encontradas)")

# ─── ALERTAS ──────────────────────────────────────────────────────────────────

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
                <p style="margin:0 0 4px;color:#64748b;font-size:13px;">PROMOCIÓN</p>
                <p style="margin:0;">{oferta['tipo_promo']}</p>
            </div>
            <a href="{oferta['url']}" style="display:block;background:#38bdf8;color:#0a1628;padding:14px;border-radius:10px;text-decoration:none;font-weight:700;text-align:center;">Ver oferta ahora →</a>
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

# ─── MONITOR ──────────────────────────────────────────────────────────────────

def monitorear():
    print("=" * 55)
    print(f"DEAL TRAVEL - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 55)

    # Marcar inactivas las de más de 7 días
    marcar_inactivas_viejas()

    todas = []
    todas.extend(scrape_mercadolibre())
    todas.extend(scrape_amazon())
    todas.extend(scrape_nike())
    todas.extend(scrape_adidas())
    todas.extend(scrape_walmart())
    todas.extend(scrape_shein())
    todas.extend(scrape_aliexpress())
    todas.extend(scrape_awin_viajes())

    print(f"TOTAL encontradas: {len(todas)}")
    guardar_en_supabase(todas)
    revisar_alertas(todas)
    return todas

if __name__ == "__main__":
    print("Deal Travel Scraper v3 — Acumulación inteligente")
    monitorear()
    schedule.every(1).hours.do(monitorear)
    schedule.every().day.at("07:00").do(monitorear)
    schedule.every().day.at("13:00").do(monitorear)
    schedule.every().day.at("19:00").do(monitorear)
    print("Monitoreo activo. Ctrl+C para detener.")
    while True:
        schedule.run_pending()
        time.sleep(60)
