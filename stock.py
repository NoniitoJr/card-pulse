import json, os, re, urllib.request, urllib.error

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
TEST = os.environ.get("TEST", "") == "true"
MI_ID = "530931920398319657"
MENCION = f"<@{MI_ID}>"

PRODUCTOS = [
    {"nombre": "ETB 30 Aniversario (Líder)", "url": "https://www.lider.cl/ip/kidults/caja-30-aniversario-elite-trainer-box-ingles/00019621415880"},
    {"nombre": "ETB 30 Aniversario (Paris)", "url": "https://www.paris.cl/juego-de-cartas-pokemon-30th-elite-trainer-box-english-574897999.html"},
    {"nombre": "Tech Sticker 30 Aniversario (Líder)", "url": "https://www.lider.cl/ip/f/pokemon-caja-30-aniversario-tech-sticker-ingles/00019621415877"},
    {"nombre": "Binder Collection 30 Aniversario (Líder)", "url": "https://super.lider.cl/ip/jugueteria/caja-30-aniversario-binder-collection-ingles/00019621415867"},
    {"nombre": "Ex Box 30 Aniversario (Líder)", "url": "https://www.lider.cl/ip/kidults/caja-30-aniversario-ex-box-ingles-1u-surtido/00019621415872"},
    {"nombre": "TV TCL 32 QLED (Líder)", "url": "https://super.lider.cl/ip/00692173289492"},
    {"nombre": "Celebraciones del 25 aniversario de Pokémon en Elite Trainer Box", "url": "https://www.lider.cl/ip/juegos-de-mesa/celebraciones-del-25-aniversario-de-pokemon-en-elite-trainer-box/00009771253157?from=/search"},
]

SI_HAY = ["agregar al carro", "añadir al carro", "agregar al carrito", "comprar ahora"]
NO_HAY = ["agotado", "sin stock", "no disponible"]
SCHEMA_SI = {"instock", "limitedavailability", "onlineonly", "preorder", "presale"}
SCHEMA_NO = {"outofstock", "soldout", "discontinued"}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def enviar(texto):
    req = urllib.request.Request(
        WEBHOOK,
        data=json.dumps({"content": texto}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": UA},
    )
    urllib.request.urlopen(req, timeout=20)


def hay_stock(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore").lower()
    except Exception as e:
        print("No pude leer", url, e)
        return None
    m = re.search(r'"availability":"https?://schema\.org/(\w+)"', html)
    schema = m.group(1) if m else None
    print("   schema:", schema)
    if schema in SCHEMA_SI:
        return True
    if schema in SCHEMA_NO:
        return False
    if any(p in html for p in NO_HAY):
        return False
    return any(p in html for p in SI_HAY)


try:
    estado = json.load(open("state.json"))
except Exception:
    estado = {}

if TEST:
    enviar(f"{MENCION} ✅ Prueba: si te suena esto en el teléfono, las alertas funcionan.")

for p in PRODUCTOS:
    ahora = hay_stock(p["url"])
    antes = estado.get(p["url"], False)
    print(p["nombre"], "->", ahora)
    if ahora is None:
        continue
    if ahora and not antes:
        enviar(f"{MENCION} 🔔 ¡HAY STOCK! {p['nombre']}\n{p['url']}")
    estado[p["url"]] = ahora

json.dump(estado, open("state.json", "w"), indent=1)
