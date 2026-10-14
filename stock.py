import json, os, urllib.request, urllib.error

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
TEST = os.environ.get("TEST", "") == "true"

# Aquí van los productos que quieres vigilar
PRODUCTOS = [
    {"nombre": "Ejemplo: caja Pokémon", "url": "https://PEGA-AQUI-EL-LINK"},
]

SI_HAY = ["agregar al carro", "añadir al carro", "agregar al carrito", "comprar ahora"]
NO_HAY = ["agotado", "sin stock", "no disponible"]
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
        return None  # desconocido: no cambia el estado
    if any(p in html for p in NO_HAY):
        return False
    return any(p in html for p in SI_HAY)


try:
    estado = json.load(open("state.json"))
except Exception:
    estado = {}

if TEST:
    enviar("✅ Prueba: el bot de restock está conectado a Discord.")

for p in PRODUCTOS:
    ahora = hay_stock(p["url"])
    antes = estado.get(p["url"], False)
    print(p["nombre"], "->", ahora)
    if ahora is None:
        continue
    if ahora and not antes:
        enviar(f"🔔 ¡HAY STOCK! {p['nombre']}\n{p['url']}")
    estado[p["url"]] = ahora

json.dump(estado, open("state.json", "w"), indent=1)
