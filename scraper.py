import os, time, re, schedule, requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SUPABASE_URL   = "https://zutcsoloxabwtrvfzmlm.supabase.co"
SUPABASE_KEY   = "sb_publishable_5TNTtixQcRsdbS_kmojIOA_6TNjtiLT"
PRECIO_MAX_MXN = 50000
AWIN_ID        = "2876425"
AMAZON_TAG     = "dealtravelmx-20"

TIENDAS_FIJAS = ["Nike MX","Adidas MX","Puma MX","Zara MX","H&M MX","Trivago","Kiwi","Sirenis Hotels","Amazon MX","Mercado Libre"]

CATEGORIAS_KEYWORDS = {
    "electronico": ["celular","iphone","samsung","laptop","tablet","tv","audifonos","smartwatch","nintendo","playstation","xbox","camara","apple","macbook","ipad"],
    "moda": ["ropa","zapatos","tenis","vestido","camisa","pantalon","bolsa","nike","adidas","zara","puma","shein","lacoste"],
    "hogar": ["sofa","cama","colchon","cocina","refrigerador","lavadora","microondas","licuadora","mueble"],
    "deporte": ["pesas","bicicleta","yoga","running","gym","proteina","futbol"],
    "belleza": ["perfume","crema","maquillaje","shampoo","serum","labial"],
    "juguetes": ["juguete","lego","barbie","hot wheels","muneca","peluche"],
    "viajes": ["hotel","vuelo","viaje","hospedaje","resort","vacaciones"],
}

def detectar_categoria(texto):
    texto_lower = texto.lower()
    for cat, keywords in CATEGORIAS_KEYWORDS.items():
        if any(kw in texto_lower for kw in keywords):
            return cat
    return "general"

def oferta_ya_existe(destino, precio, fuente):
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        term = requests.utils.quote(destino[:25])
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/ofertas?destino=ilike.*{term}*&precio=eq.{precio}&fuente=eq.{fuente}",
            headers=headers, timeout=10
        )
        return len(r.json()) > 0
    except:
        return False

def scrape_amazon():
    """Productos reales de Amazon con links de afiliado directos"""
    ofertas = []
    productos = [
        ("Apple iPhone 15 128GB", 14999, "electronico", "iphone+15+128gb"),
        ("Samsung Galaxy S24 256GB", 13999, "electronico", "samsung+galaxy+s24"),
        ("MacBook Air M2 256GB", 23999, "electronico", "macbook+air+m2"),
        ("iPad 10ma generación 64GB", 8999, "electronico", "ipad+10+generacion"),
        ("Sony WH-1000XM5 Audífonos", 5999, "electronico", "sony+wh1000xm5"),
        ("Nintendo Switch OLED", 7999, "electronico", "nintendo+switch+oled"),
        ("Samsung Smart TV 55\" 4K", 9999, "electronico", "samsung+smart+tv+55"),
        ("Laptop HP 15 Core i5 8GB", 9499, "electronico", "laptop+hp+core+i5"),
        ("PlayStation 5 Slim", 11999, "electronico", "playstation+5+slim"),
        ("Apple Watch Series 9", 7499, "electronico", "apple+watch+series+9"),
        ("Cafetera Nespresso Vertuo", 2499, "hogar", "cafetera+nespresso+vertuo"),
        ("Instant Pot Duo 7 en 1", 1899, "hogar", "instant+pot+duo"),
        ("Roomba i3 Aspiradora Robot", 4999, "hogar", "roomba+i3"),
        ("Perfume Carolina Herrera Good Girl", 1899, "belleza", "carolina+herrera+good+girl"),
        ("Crema Facial CeraVe Hidratante", 299, "belleza", "cerave+crema+facial"),
        ("Tenis Nike Air Max 270 Hombre", 2199, "moda", "nike+air+max+270"),
        ("Mochila Samsonite 20L", 899, "moda", "mochila+samsonite"),
        ("Báscula Digital Xiaomi", 399, "hogar", "bascula+digital+xiaomi"),
    ]
    for nombre, precio, tipo, query in productos:
        ofertas.append({
            "fuente": "Amazon MX",
            "tipo": tipo,
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "url": f"https://www.amazon.com.mx/s?k={query}&tag={AMAZON_TAG}",
            "tipo_promo": "Oferta Amazon",
            "palabras_clave": query.replace("+", ", "),
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Amazon MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_mercadolibre():
    ofertas = []
    busquedas = [
        ("laptop", "electronico"),
        ("iphone", "electronico"),
        ("samsung", "electronico"),
        ("tenis nike", "moda"),
        ("tenis adidas", "moda"),
        ("television", "electronico"),
        ("audifonos", "electronico"),
        ("refrigerador", "hogar"),
        ("perfume", "belleza"),
        ("nintendo switch", "electronico"),
    ]
    for query, tipo in busquedas:
        try:
            url = f"https://api.mercadolibre.com/sites/MLM/search?q={requests.utils.quote(query)}&sort=relevance&limit=5"
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                continue
            data = r.json()
            for item in data.get("results", []):
                precio = item.get("price", 0)
                original = item.get("original_price") or 0
                if not (200 <= precio <= PRECIO_MAX_MXN):
                    continue
                if original <= precio:
                    continue
                descuento = round((1 - precio / original) * 100)
                if descuento < 5:
                    continue
                ofertas.append({
                    "fuente": "Mercado Libre",
                    "tipo": tipo,
                    "destino": item["title"][:80],
                    "precio": precio,
                    "precio_fmt": f"${precio:,.0f} MXN",
                    "url": item["permalink"],
                    "tipo_promo": f"-{descuento}% descuento",
                    "palabras_clave": query,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "activa": True
                })
        except Exception as e:
            print(f"[MercadoLibre] Error {query}: {e}")
    print(f"[Mercado Libre] {len(ofertas)} ofertas")
    return ofertas

def scrape_nike():
    ofertas = []
    productos = [
        ("Nike Air Max 270", 2499, "tenis, running, nike"),
        ("Nike Revolution 6", 1299, "tenis, running, nike"),
        ("Nike Dri-FIT Camiseta", 699, "ropa deportiva, nike"),
        ("Nike Air Force 1", 1999, "tenis, nike, casual"),
        ("Nike Zoom Pegasus", 2899, "running, tenis, nike"),
        ("Nike Flex Experience", 1499, "tenis, gym, nike"),
        ("Nike Pro Shorts", 599, "ropa deportiva, nike, gym"),
        ("Nike Brasilia Mochila", 899, "accesorios, nike"),
    ]
    for nombre, precio, keywords in productos:
        ofertas.append({
            "fuente": "Nike MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "url": "https://www.nike.com/mx/w/sale-3yaep",
            "tipo_promo": "Sale Nike MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Nike MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_adidas():
    ofertas = []
    productos = [
        ("Adidas Ultraboost 22", 3299, "tenis, running, adidas"),
        ("Adidas Stan Smith", 1799, "tenis, casual, adidas"),
        ("Adidas Superstar", 1599, "tenis, casual, adidas"),
        ("Adidas Tiro Pants", 799, "ropa deportiva, adidas, gym"),
        ("Adidas Forum Low", 1899, "tenis, casual, adidas"),
        ("Adidas Entrada Jersey", 499, "ropa deportiva, futbol, adidas"),
        ("Adidas Essentials Hoodie", 999, "ropa, adidas, casual"),
        ("Adidas Predator Accuracy", 2499, "tenis futbol, adidas"),
    ]
    for nombre, precio, keywords in productos:
        ofertas.append({
            "fuente": "Adidas MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "url": "https://www.adidas.mx/sale",
            "tipo_promo": "Sale Adidas MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Adidas MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_puma():
    ofertas = []
    productos = [
        ("Puma Suede Classic XXI", 1299, "tenis, casual, puma"),
        ("Puma RS-X", 1599, "tenis, casual, puma"),
        ("Puma Camiseta Teamliga", 449, "ropa, futbol, puma"),
        ("Puma Softride Enzo", 1199, "tenis, running, puma"),
        ("Puma Essentials Hoodie", 799, "ropa, casual, puma"),
    ]
    for nombre, precio, keywords in productos:
        ofertas.append({
            "fuente": "Puma MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "url": "https://mx.puma.com/es/sale",
            "tipo_promo": "Sale Puma MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Puma MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_zara():
    ofertas = []
    productos = [
        ("Zara Blazer Oversized", 1299, "ropa, moda, zara, mujer"),
        ("Zara Jeans Slim", 799, "pantalon, moda, zara"),
        ("Zara Vestido Midi", 999, "vestido, moda, zara, mujer"),
        ("Zara Camisa Oversize", 699, "camisa, moda, zara"),
        ("Zara Zapatillas Piel", 1499, "zapatos, moda, zara, mujer"),
        ("Zara Bolso Tote", 899, "bolsa, accesorios, zara"),
    ]
    for nombre, precio, keywords in productos:
        ofertas.append({
            "fuente": "Zara MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "url": "https://www.zara.com/mx/es/sale-l1000.html",
            "tipo_promo": "Sale Zara MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Zara MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_hm():
    ofertas = []
    productos = [
        ("H&M Vestido Floral", 499, "vestido, moda, hm, mujer"),
        ("H&M Jeans Skinny", 599, "pantalon, moda, hm"),
        ("H&M Camiseta Basica", 199, "camiseta, moda, hm"),
        ("H&M Sudadera Logo", 699, "ropa, casual, hm"),
        ("H&M Chaqueta Denim", 899, "ropa, casual, hm"),
    ]
    for nombre, precio, keywords in productos:
        ofertas.append({
            "fuente": "H&M MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "url": "https://www2.hm.com/es_mx/sale.html",
            "tipo_promo": "Sale H&M MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[H&M MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_awin_viajes():
    ofertas = []
    destinos_trivago = [
        ("Cancún, México", 1200),
        ("Ciudad de México", 800),
        ("Los Cabos", 1500),
        ("Puerto Vallarta", 1100),
        ("Playa del Carmen", 1300),
        ("Tulum", 1400),
        ("Oaxaca", 900),
        ("Guadalajara", 850),
    ]
    for destino, precio in destinos_trivago:
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
    vuelos_kiwi = [
        ("CDMX → Cancún", 1800),
        ("CDMX → Los Cabos", 2100),
        ("CDMX → Guadalajara", 900),
        ("CDMX → Monterrey", 950),
        ("CDMX → Miami", 4500),
        ("CDMX → Nueva York", 5200),
        ("CDMX → Madrid", 7800),
        ("CDMX → Bogotá", 4200),
    ]
    for ruta, precio in vuelos_kiwi:
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
    sirenis = [
        ("Sirenis Punta Cana Resort — Todo Incluido", 3200),
        ("Sirenis Riviera Maya — Todo Incluido", 2800),
        ("Sirenis Tropical Suites Tenerife", 2500),
    ]
    for nombre, precio in sirenis:
        ofertas.append({
            "fuente": "Sirenis Hotels",
            "tipo": "viajes",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN/noche",
            "url": f"https://www.awin1.com/cread.php?s=3330897&v=20563&q=474350&r={AWIN_ID}&ued=https://www.sirenishotels.com",
            "tipo_promo": "Todo incluido desde",
            "palabras_clave": "hotel, resort, todo incluido, sirenis",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Awin Viajes] {len(ofertas)} ofertas")
    return ofertas

def marcar_inactivas_viejas():
    headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    TIENDAS_SCRAPER = [
        "Amazon MX","Mercado Libre","Nike MX","Adidas MX",
        "Puma MX","Zara MX","H&M MX","Trivago","Kiwi","Sirenis Hotels"
    ]
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
            es_fija = oferta["fuente"] in TIENDAS_FIJAS
            if es_fija or not oferta_ya_existe(oferta["destino"], oferta["precio"], oferta["fuente"]):
                r = requests.post(
                    f"{SUPABASE_URL}/rest/v1/ofertas",
                    headers=headers,
                    json=oferta,
                    timeout=10
                )
                if r.status_code in [200, 201]:
                    nuevas += 1
        except Exception as e:
            print(f"[Supabase] Error: {e}")
    print(f"[Supabase] {nuevas} ofertas nuevas guardadas (de {len(ofertas)} encontradas)")

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

def monitorear():
    print("=" * 55)
    print(f"DEAL TRAVEL - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 55)
    marcar_inactivas_viejas()
    todas = []
    todas.extend(scrape_amazon())
    todas.extend(scrape_mercadolibre())
    todas.extend(scrape_nike())
    todas.extend(scrape_adidas())
    todas.extend(scrape_puma())
    todas.extend(scrape_zara())
    todas.extend(scrape_hm())
    todas.extend(scrape_awin_viajes())
    print(f"TOTAL encontradas: {len(todas)}")
    guardar_en_supabase(todas)
    revisar_alertas(todas)
    return todas

if __name__ == "__main__":
    print("Deal Travel Scraper v6")
    monitorear()
    schedule.every(1).hours.do(monitorear)
    schedule.every().day.at("07:00").do(monitorear)
    schedule.every().day.at("13:00").do(monitorear)
    schedule.every().day.at("19:00").do(monitorear)
    print("Monitoreo activo. Ctrl+C para detener.")
    while True:
        schedule.run_pending()
        time.sleep(60)
