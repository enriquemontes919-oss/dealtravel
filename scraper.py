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
EXPEDIA_LINK   = "https://www.awin1.com/cread.php?awinmid=117689&awinaffid=2876425&ued=https%3A%2F%2Fwww.expedia.mx%2FHotels"
HOTELES_LINK   = "https://www.awin1.com/cread.php?awinmid=117687&awinaffid=2876425&ued=https%3A%2F%2Fwww.hoteles.com"

TIENDAS_FIJAS = ["Nike MX","Adidas MX","Puma MX","Zara MX","H&M MX","Trivago","Kiwi","Sirenis Hotels","Amazon MX","Mercado Libre","Expedia MX","Hoteles.com MX"]

CATEGORIAS_KEYWORDS = {
    "electronico": ["celular","iphone","samsung","laptop","tablet","tv","audifonos","smartwatch","nintendo","playstation","xbox","camara","apple","macbook","ipad"],
    "moda": ["ropa","zapatos","tenis","vestido","camisa","pantalon","bolsa","nike","adidas","zara","puma","shein","lacoste"],
    "hogar": ["sofa","cama","colchon","cocina","refrigerador","lavadora","microondas","licuadora","mueble"],
    "deporte": ["pesas","bicicleta","yoga","running","gym","proteina","futbol"],
    "belleza": ["perfume","crema","maquillaje","shampoo","serum","labial"],
    "juguetes": ["juguete","lego","barbie","hot wheels","muneca","peluche"],
    "viajes": ["hotel","vuelo","viaje","hospedaje","resort","vacaciones"],
}

MESES_ES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

def generar_fechas_viaje(indice):
    hoy = datetime.now()
    dias_hasta_viernes = (4 - hoy.weekday()) % 7
    if dias_hasta_viernes == 0:
        dias_hasta_viernes = 7
    viernes = hoy + timedelta(days=dias_hasta_viernes)
    domingo = viernes + timedelta(days=2)
    en_2_semanas = hoy + timedelta(days=14)
    en_3_semanas = hoy + timedelta(days=21)
    en_1_mes = hoy + timedelta(days=30)
    en_5_semanas = hoy + timedelta(days=37)
    def fmt(d):
        return f"{d.day} {MESES_ES[d.month - 1]}"
    rangos = [
        f"{fmt(viernes)} – {fmt(domingo)}",
        f"{fmt(en_2_semanas)} – {fmt(en_3_semanas)}",
        f"{fmt(en_1_mes)} – {fmt(en_5_semanas)}",
    ]
    return rangos[indice % 3]

def precio_original(precio, descuento_pct):
    return round(precio / (1 - descuento_pct / 100))

def amazon_url(asin):
    return f"https://www.amazon.com.mx/dp/{asin}?tag={AMAZON_TAG}"

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
    ofertas = []
    # Electrónicos, hogar y belleza → sin precio fijo (precio=0, precio_fmt="Ver precio")
    # Moda de Amazon → mantiene precio y descuento
    productos = [
        # (nombre, precio, descuento%, tipo, asin)
        # Electrónicos — sin precio
        ("Apple iPhone 15 128GB",            0, 0,  "electronico", "B0CHX8VZ2N"),
        ("Samsung Galaxy S24 256GB",         0, 0,  "electronico", "B0CQ7R738Y"),
        ("MacBook Air M2 256GB",             0, 0,  "electronico", "B0B3C1N9FY"),
        ("iPad 10ma generación 64GB",        0, 0,  "electronico", "B0BJLF2BRM"),
        ("Sony WH-1000XM5 Audífonos",        0, 0,  "electronico", "B09XS7JWHH"),
        ("Nintendo Switch OLED",             0, 0,  "electronico", "B098RKWHHZ"),
        ("Samsung Smart TV 55\" 4K",         0, 0,  "electronico", "B0BN7FYKQM"),
        ("Laptop HP 15 Core i5 8GB",         0, 0,  "electronico", "B0BX5CPGX5"),
        ("PlayStation 5 Slim",              0, 0,  "electronico", "B0CL61F39H"),
        ("Apple Watch Series 9",             0, 0,  "electronico", "B0CHX8H5LQ"),
        # Hogar — sin precio
        ("Cafetera Nespresso Vertuo",        0, 0,  "hogar",       "B07THHQMHM"),
        ("Instant Pot Duo 7 en 1",           0, 0,  "hogar",       "B00FLYWNYQ"),
        ("Roomba i3 Aspiradora Robot",       0, 0,  "hogar",       "B08H6NJBJ7"),
        ("Báscula Digital Xiaomi",           0, 0,  "hogar",       "B07H243WM8"),
        # Belleza — sin precio
        ("Perfume Carolina Herrera Good Girl", 0, 0, "belleza",    "B01N1WJUQ6"),
        ("Crema Facial CeraVe Hidratante",   0, 0,  "belleza",     "B000YJ2SKS"),
        # Moda — mantiene precio y descuento
        ("Tenis Nike Air Max 270 Hombre",    2199, 25, "moda",      "B07D26TJ58"),
        ("Mochila Samsonite 20L",             899, 20, "moda",      "B082NKS553"),
    ]
    for nombre, precio, descuento, tipo, asin in productos:
        sin_precio = precio == 0
        orig = precio_original(precio, descuento) if not sin_precio and descuento > 0 else None
        ofertas.append({
            "fuente": "Amazon MX",
            "tipo": tipo,
            "destino": nombre,
            "precio": precio,
            "precio_fmt": "Ver precio" if sin_precio else f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct": descuento if not sin_precio else None,
            "url": amazon_url(asin),
            "tipo_promo": "Oferta Amazon" if sin_precio else f"-{descuento}% Oferta Amazon",
            "palabras_clave": nombre.lower(),
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
                    "precio_original": round(original),
                    "descuento_pct": descuento,
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
        ("Nike Air Max 270", 2499, 20, "tenis, running, nike"),
        ("Nike Revolution 6", 1299, 25, "tenis, running, nike"),
        ("Nike Dri-FIT Camiseta", 699, 30, "ropa deportiva, nike"),
        ("Nike Air Force 1", 1999, 20, "tenis, nike, casual"),
        ("Nike Zoom Pegasus", 2899, 15, "running, tenis, nike"),
        ("Nike Flex Experience", 1499, 25, "tenis, gym, nike"),
        ("Nike Pro Shorts", 599, 30, "ropa deportiva, nike, gym"),
        ("Nike Brasilia Mochila", 899, 20, "accesorios, nike"),
    ]
    for nombre, precio, descuento, keywords in productos:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "Nike MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": "https://www.nike.com/mx/w/sale-3yaep",
            "tipo_promo": f"-{descuento}% Sale Nike MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Nike MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_adidas():
    ofertas = []
    productos = [
        ("Adidas Ultraboost 22", 3299, 25, "tenis, running, adidas"),
        ("Adidas Stan Smith", 1799, 20, "tenis, casual, adidas"),
        ("Adidas Superstar", 1599, 20, "tenis, casual, adidas"),
        ("Adidas Tiro Pants", 799, 30, "ropa deportiva, adidas, gym"),
        ("Adidas Forum Low", 1899, 20, "tenis, casual, adidas"),
        ("Adidas Entrada Jersey", 499, 35, "ropa deportiva, futbol, adidas"),
        ("Adidas Essentials Hoodie", 999, 25, "ropa, adidas, casual"),
        ("Adidas Predator Accuracy", 2499, 20, "tenis futbol, adidas"),
    ]
    for nombre, precio, descuento, keywords in productos:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "Adidas MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": "https://www.adidas.mx/sale",
            "tipo_promo": f"-{descuento}% Sale Adidas MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Adidas MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_puma():
    ofertas = []
    productos = [
        ("Puma Suede Classic XXI", 1299, 20, "tenis, casual, puma"),
        ("Puma RS-X", 1599, 25, "tenis, casual, puma"),
        ("Puma Camiseta Teamliga", 449, 30, "ropa, futbol, puma"),
        ("Puma Softride Enzo", 1199, 20, "tenis, running, puma"),
        ("Puma Essentials Hoodie", 799, 25, "ropa, casual, puma"),
    ]
    for nombre, precio, descuento, keywords in productos:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "Puma MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": "https://mx.puma.com/es/sale",
            "tipo_promo": f"-{descuento}% Sale Puma MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Puma MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_zara():
    ofertas = []
    productos = [
        ("Zara Blazer Oversized", 1299, 30, "ropa, moda, zara, mujer", "https://www.zara.com/mx/es/mujer-blazers-oversize-l4189.html"),
        ("Zara Jeans Slim", 799, 20, "pantalon, moda, zara", "https://www.zara.com/mx/es/mujer-jeans-slim-l1280.html"),
        ("Zara Vestido Midi", 999, 25, "vestido, moda, zara, mujer", "https://www.zara.com/mx/es/mujer-vestidos-midi-l1303.html"),
        ("Zara Camisa Oversize", 699, 30, "camisa, moda, zara", "https://www.zara.com/mx/es/mujer-camisas-l1217.html"),
        ("Zara Zapatillas Piel", 1499, 20, "zapatos, moda, zara, mujer", "https://www.zara.com/mx/es/mujer-zapatos-l1251.html"),
        ("Zara Bolso Tote", 899, 25, "bolsa, accesorios, zara", "https://www.zara.com/mx/es/mujer-bolsos-tote-l1025.html"),
    ]
    for nombre, precio, descuento, keywords, url in productos:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "Zara MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": url,
            "tipo_promo": f"-{descuento}% Sale Zara MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[Zara MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_hm():
    ofertas = []
    productos = [
        ("H&M Vestido Floral", 499, 30, "vestido, moda, hm, mujer", "https://www2.hm.com/es_mx/mujer/productos/vestidos/vestidos-floral.html"),
        ("H&M Jeans Skinny", 599, 25, "pantalon, moda, hm", "https://www2.hm.com/es_mx/mujer/productos/jeans/jeans-skinny.html"),
        ("H&M Camiseta Basica", 199, 30, "camiseta, moda, hm", "https://www2.hm.com/es_mx/mujer/productos/camisetas-y-tops/camisetas.html"),
        ("H&M Sudadera Logo", 699, 20, "ropa, casual, hm", "https://www2.hm.com/es_mx/mujer/productos/sudaderas-y-hoodies.html"),
        ("H&M Chaqueta Denim", 899, 25, "ropa, casual, hm", "https://www2.hm.com/es_mx/mujer/productos/chaquetas-y-abrigos/chaquetas-denim.html"),
    ]
    for nombre, precio, descuento, keywords, url in productos:
        orig = precio_original(precio, descuento)
        ofertas.append({
            "fuente": "H&M MX",
            "tipo": "moda",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": url,
            "tipo_promo": f"-{descuento}% Sale H&M MX",
            "palabras_clave": keywords,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    print(f"[H&M MX] {len(ofertas)} ofertas")
    return ofertas

def scrape_awin_viajes():
    ofertas = []
    destinos_trivago = [
        ("Cancún, México", 1200, 20),
        ("Ciudad de México", 800, 15),
        ("Los Cabos", 1500, 25),
        ("Puerto Vallarta", 1100, 20),
        ("Playa del Carmen", 1300, 22),
        ("Tulum", 1400, 18),
        ("Oaxaca", 900, 15),
        ("Guadalajara", 850, 20),
    ]
    for i, (destino, precio, descuento) in enumerate(destinos_trivago):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Trivago",
            "tipo": "viajes",
            "destino": f"Hotel en {destino}",
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN/noche",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": f"https://www.awin1.com/cread.php?s=3330897&v=20563&q=474350&r={AWIN_ID}&ued=https://www.trivago.com.mx/?search/200-{destino.replace(' ','%20')}",
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "hotel, viaje, hospedaje, trivago",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    vuelos_kiwi = [
        ("CDMX → Cancún", 1800, 15),
        ("CDMX → Los Cabos", 2100, 18),
        ("CDMX → Guadalajara", 900, 20),
        ("CDMX → Monterrey", 950, 15),
        ("CDMX → Miami", 4500, 22),
        ("CDMX → Nueva York", 5200, 20),
        ("CDMX → Madrid", 7800, 25),
        ("CDMX → Bogotá", 4200, 18),
    ]
    for i, (ruta, precio, descuento) in enumerate(vuelos_kiwi):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Kiwi",
            "tipo": "viajes",
            "destino": f"Vuelo {ruta}",
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": f"https://www.awin1.com/cread.php?s=2702014&v=20563&q=395852&r={AWIN_ID}",
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "vuelo, avion, kiwi, viaje",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    sirenis = [
        ("Sirenis Punta Cana Resort — Todo Incluido", 3200, 25),
        ("Sirenis Riviera Maya — Todo Incluido", 2800, 20),
        ("Sirenis Tropical Suites Tenerife", 2500, 18),
    ]
    for i, (nombre, precio, descuento) in enumerate(sirenis):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Sirenis Hotels",
            "tipo": "viajes",
            "destino": nombre,
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN/noche",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": f"https://www.awin1.com/cread.php?s=3330897&v=20563&q=474350&r={AWIN_ID}&ued=https://www.sirenishotels.com",
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "hotel, resort, todo incluido, sirenis",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    destinos_expedia = [
        ("Cancún", 1350, 20),
        ("Los Cabos", 1800, 25),
        ("Puerto Vallarta", 1250, 18),
        ("Ciudad de México", 950, 15),
        ("Playa del Carmen", 1450, 22),
        ("Tulum", 1600, 20),
        ("Oaxaca", 1050, 15),
        ("Guadalajara", 980, 18),
    ]
    for i, (destino, precio, descuento) in enumerate(destinos_expedia):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Expedia MX",
            "tipo": "viajes",
            "destino": f"Hotel en {destino} — Expedia",
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN/noche",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": EXPEDIA_LINK,
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "hotel, viaje, hospedaje, expedia",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "activa": True
        })
    destinos_hoteles = [
        ("Cancún", 1300, 20),
        ("Los Cabos", 1750, 22),
        ("Puerto Vallarta", 1200, 18),
        ("Ciudad de México", 900, 15),
        ("Playa del Carmen", 1400, 20),
        ("Tulum", 1550, 25),
        ("Oaxaca", 1000, 15),
        ("Monterrey", 950, 18),
    ]
    for i, (destino, precio, descuento) in enumerate(destinos_hoteles):
        orig = precio_original(precio, descuento)
        fechas = generar_fechas_viaje(i)
        ofertas.append({
            "fuente": "Hoteles.com MX",
            "tipo": "viajes",
            "destino": f"Hotel en {destino} — Hoteles.com",
            "precio": precio,
            "precio_fmt": f"${precio:,.0f} MXN/noche",
            "precio_original": orig,
            "descuento_pct": descuento,
            "url": HOTELES_LINK,
            "tipo_promo": f"-{descuento}% · {fechas}",
            "palabras_clave": "hotel, viaje, hospedaje, hoteles.com",
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
        "Puma MX","Zara MX","H&M MX","Trivago","Kiwi","Sirenis Hotels",
        "Expedia MX","Hoteles.com MX"
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

def revisar_alertas(todas_ofertas):
    if not RESEND_API_KEY:
        return
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        r = requests.get(f"{SUPABASE_URL}/rest/v1/alertas?activa=eq.true&select=*", headers=headers)
        alertas = r.json()
        print(f"[Alertas] {len(alertas)} alertas activas")
        r2 = requests.get(f"{SUPABASE_URL}/rest/v1/ofertas?activa=eq.true&select=*", headers=headers)
        ofertas_supabase = r2.json()
        print(f"[Ofertas] {len(ofertas_supabase)} ofertas en Supabase")
        ahora = datetime.now()
        for alerta in alertas:
            try:
                dias_alerta = alerta.get("dias_alerta") or 7
                fecha_creacion = datetime.fromisoformat(alerta["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                dias_transcurridos = (ahora - fecha_creacion).days
                if dias_transcurridos >= dias_alerta:
                    requests.patch(
                        f"{SUPABASE_URL}/rest/v1/alertas?id=eq.{alerta['id']}",
                        headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                        json={"activa": False}, timeout=10
                    )
                    print(f"[Alertas] Alerta {alerta['id']} expirada")
                    continue
                ya_notificados = set(alerta.get("ofertas_notificadas") or [])
                producto_alerta = alerta.get("destino", "").lower()
                palabras_alerta = [w for w in producto_alerta.split() if len(w) > 2]
                presupuesto = float(alerta.get("presupuesto") or 99999)
                fuente_alerta = alerta.get("fuente", "Cualquier tienda")
                matches_nuevos = []
                for oferta in ofertas_supabase:
                    if oferta["id"] in ya_notificados:
                        continue
                    producto_oferta = oferta.get("destino", "").lower()
                    # Para productos sin precio (precio=0), siempre pasan el filtro de presupuesto
                    precio_ok = oferta["precio"] == 0 or oferta["precio"] <= presupuesto
                    tienda_ok = not fuente_alerta or fuente_alerta == "Cualquier tienda" or fuente_alerta.lower() in oferta["fuente"].lower()
                    producto_match = any(word in producto_oferta for word in palabras_alerta)
                    if precio_ok and tienda_ok and producto_match:
                        matches_nuevos.append(oferta)
                if not matches_nuevos:
                    print(f"[Alertas] Alerta {alerta['id']} — sin ofertas nuevas")
                    continue
                print(f"[Match] {alerta['email']} -> {len(matches_nuevos)} ofertas NUEVAS")
                enviar_email_consolidado(alerta, matches_nuevos, dias_alerta, dias_transcurridos)
                nuevos_ids = list(ya_notificados) + [o["id"] for o in matches_nuevos]
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/alertas?id=eq.{alerta['id']}",
                    headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                    json={"ultimo_envio": ahora.isoformat(), "ofertas_notificadas": nuevos_ids},
                    timeout=10
                )
            except Exception as e:
                print(f"[Alertas] Error procesando alerta {alerta.get('id')}: {e}")
    except Exception as e:
        print(f"[Alertas] Error general: {e}")

def enviar_email_consolidado(alerta, ofertas, dias_alerta, dias_transcurridos):
    dias_restantes = dias_alerta - dias_transcurridos
    ofertas_html = ""
    for oferta in ofertas[:8]:
        precio_orig = oferta.get("precio_original")
        descuento = oferta.get("descuento_pct")
        sin_precio = oferta.get("precio_fmt") == "Ver precio"
        precio_orig_html = ""
        if not sin_precio and precio_orig and precio_orig > oferta["precio"]:
            precio_orig_html = f'<span style="text-decoration:line-through;color:#aeaeb2;font-size:0.8rem;">${precio_orig:,.0f}</span> '
        descuento_badge = ""
        if not sin_precio and descuento:
            descuento_badge = f'<span style="background:#ff3b30;color:#fff;font-size:0.65rem;font-weight:700;padding:2px 7px;border-radius:6px;margin-left:6px;">-{descuento}%</span>'
        precio_display = f'<span style="font-size:1.1rem;font-weight:700;color:#0071e3;">Ver precio en Amazon →</span>' if sin_precio else f'<span style="font-size:1.4rem;font-weight:800;color:#0ea5e9;">{oferta["precio_fmt"]}</span>'
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
            <p style="color:rgba(255,255,255,0.6);margin:0;font-size:0.85rem;">Encontramos {len(ofertas)} oferta{'s' if len(ofertas) > 1 else ''} nuevas para ti</p>
        </div>
        <div style="background:#fff;padding:24px;border-radius:0 0 12px 12px;">
            <div style="background:#f0f8ff;border:1px solid #cce5ff;border-radius:10px;padding:12px 16px;margin-bottom:20px;">
                <p style="margin:0;font-size:0.85rem;color:#0071e3;">
                    🔔 Tu alerta: <strong>{alerta['destino']}</strong> · 
                    Presupuesto: <strong>${float(alerta.get('presupuesto', 0)):,.0f} MXN</strong> · 
                    <span style="color:#64748b;">Vence en {dias_restantes} día{'s' if dias_restantes != 1 else ''}</span>
                </p>
            </div>
            {ofertas_html}
            <div style="text-align:center;margin-top:20px;padding-top:16px;border-top:1px solid #e2e8f0;">
                <a href="https://www.dealtravel.mx" style="background:#0071e3;color:#fff;padding:12px 24px;border-radius:980px;text-decoration:none;font-weight:600;font-size:0.9rem;">Ver todas las ofertas en dealtravel.mx</a>
            </div>
            <p style="color:#94a3b8;font-size:0.72rem;margin-top:16px;text-align:center;">
                Deal Travel · dealtravel.mx<br>
                Tu alerta expira en {dias_restantes} día{'s' if dias_restantes != 1 else ''}. 
                <a href="https://www.dealtravel.mx#alerta" style="color:#0071e3;">Renovar alerta</a>
            </p>
        </div>
    </div>"""
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={
                "from": "Deal Travel <alertas@dealtravel.mx>",
                "to": [alerta["email"]],
                "subject": f"🔥 {len(ofertas)} oferta{'s' if len(ofertas) > 1 else ''} nueva{'s' if len(ofertas) > 1 else ''} para '{alerta['destino']}' — dealtravel.mx",
                "html": html
            }
        )
        if r.status_code == 200:
            print(f"[Email] Enviado a {alerta['email']} ({len(ofertas)} ofertas nuevas)")
        else:
            print(f"[Email] Error: {r.status_code} — {r.text[:100]}")
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
    print("Deal Travel Scraper v9")
    monitorear()
    schedule.every(1).hours.do(monitorear)
    schedule.every().day.at("07:00").do(monitorear)
    schedule.every().day.at("13:00").do(monitorear)
    schedule.every().day.at("19:00").do(monitorear)
    print("Monitoreo activo. Ctrl+C para detener.")
    while True:
        schedule.run_pending()
        time.sleep(60)
