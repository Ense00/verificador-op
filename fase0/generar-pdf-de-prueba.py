#!/usr/bin/env python3
"""Genera un PDF de prueba que imita un escaneo de Órdenes de Pago.

Imita el formato real observado en un PDF de la plataforma (escáner a 200 ppp, a
color, sin capa de texto), pero con datos **ficticios**: institución inventada,
órdenes 1900000001…, nombres y montos al azar. El PDF que produce está bloqueado
en .gitignore.

    python3 fase0/generar-pdf-de-prueba.py

Trae la misma estructura que el real —cada orden seguida de su soporte— y los
casos que hacen fallar al OCR: raya de pluma encima de los dígitos, sello sobre
una firma, orden con 3, 2, 1 y 0 firmas, orden de dos hojas, una ADEFA (-A) y
otra serie (51). Requiere Pillow.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, os

random.seed(7)
W, H = 1700, 2200                       # carta a ~200 ppp
NEGRO, GRIS = (28, 30, 36), (90, 95, 105)
AZUL, ROJO = (34, 52, 140), (170, 40, 40)
F = lambda s, b=False: ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)


def papel():
    return Image.new("RGB", (W, H), (252, 251, 248))


def escanear(im, ang):
    im = im.rotate(ang, expand=False, fillcolor=(250, 249, 246), resample=Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    px = im.load()
    for _ in range(60000):
        x, y = random.randrange(W), random.randrange(H)
        v = random.randint(-22, 8)
        r, g, b = px[x, y]
        px[x, y] = (max(0, min(255, r + v)), max(0, min(255, g + v)), max(0, min(255, b + v)))
    return im


def garabato(d, x, y, ancho, alto, color=AZUL, grueso=4):
    px, py = x, y
    for i in range(1, 61):
        nx = x + ancho * i / 60 + random.randint(-7, 7)
        ny = y - abs(alto) * random.random() - alto * 0.15
        d.line([(px, py), (nx, ny)], fill=color, width=grueso)
        px, py = nx, ny


def sello(d, cx, cy, texto, color=AZUL, r=150):
    d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62], outline=color, width=5)
    d.text((cx - r * 0.72, cy - 26), texto, font=F(46, True), fill=color)


def caja_numero(d, num):
    """Caja de arriba a la derecha: rótulo 'Orden de Pago' y el número debajo."""
    x0, y0, x1, y1 = int(W * 0.72), int(H * 0.055), int(W * 0.955), int(H * 0.125)
    medio = (y0 + y1) // 2
    d.rectangle([x0, y0, x1, y1], outline=NEGRO, width=3)
    d.line([(x0, medio), (x1, medio)], fill=NEGRO, width=3)
    d.text((x0 + 60, y0 + 14), "Orden de Pago", font=F(34, True), fill=NEGRO)
    d.line([(x0 + 60, y0 + 56), (x0 + 330, y0 + 56)], fill=NEGRO, width=2)
    d.text((x0 + 90, medio + 14), num, font=F(34), fill=NEGRO)
    d.text((x0 + 120, y1 + 18), "ORIGINAL", font=F(36, True), fill=NEGRO)
    return (x0, y0, x1, y1)


def celdas_firma(d, firmas, tapar_una=False):
    """Tres celdas abajo: cargo, firma encima del nombre impreso."""
    y0, y1 = int(H * 0.82), int(H * 0.965)
    titulos = ["SOLICITANTE", "AUTORIZACIÓN DEL TITULAR", "PÁGUESE"]
    cargos = [["SUBSECRETARIO DE", "PLANEACIÓN Y ADMINISTRACIÓN"],
              ["SECRETARIO DE EDUCACIÓN", "Y CULTURA"],
              ["TESORERO", ""]]
    nombres = ["LIC. NOMBRE APELLIDO UNO", "PROFR. NOMBRE APELLIDO DOS", "C.P. NOMBRE APELLIDO TRES"]
    for i in range(3):
        x0 = int(W * (0.07 + i * 0.295)); x1 = int(W * (0.07 + i * 0.295 + 0.28))
        d.rectangle([x0, y0, x1, y1], outline=NEGRO, width=2)
        d.line([(x0, y0 + 52), (x1, y0 + 52)], fill=NEGRO, width=2)
        d.text((x0 + 24, y0 + 12), titulos[i], font=F(24, True), fill=NEGRO)
        for k, ln in enumerate(cargos[i]):
            d.text((x0 + 24, y0 + 70 + k * 30), ln, font=F(22, True), fill=NEGRO)
        d.text((x0 + 16, y1 - 34), nombres[i], font=F(21, True), fill=NEGRO)
        if i < firmas:
            garabato(d, x0 + 40, y1 - 46, x1 - x0 - 90, 70)
    if tapar_una:
        sello(d, int(W * 0.36), int(H * 0.90), "PAGADO", ROJO, 160)


def pagina_orden(num, montos, firmas, hoja=None, raya_en_numero=False, tapar_una=False):
    im = papel(); d = ImageDraw.Draw(im)
    d.text((int(W * 0.22), int(H * 0.018)), "GOBIERNO DEL ESTADO DE PRUEBA", font=F(36, True), fill=NEGRO)
    d.text((int(W * 0.30), int(H * 0.048)), "ORDEN DE PAGO", font=F(40, True), fill=NEGRO)
    d.text((int(W * 0.28), int(H * 0.078)), "SECRETARIA DE HACIENDA", font=F(26), fill=NEGRO)
    caja = caja_numero(d, num)
    if raya_en_numero:                               # el caso que rompía el OCR
        d.line([(caja[0] - 60, caja[1] - 40), (caja[2] - 40, caja[3] + 60)], fill=ROJO, width=5)
    d.text((int(W * 0.06), int(H * 0.15)), "Dependencia: DEPENDENCIA DE PRUEBA", font=F(26, True), fill=NEGRO)
    d.text((int(W * 0.06), int(H * 0.18)), "Beneficiario: 10000000 - PROVEEDOR DEMOSTRATIVO", font=F(24), fill=NEGRO)
    if hoja:
        d.text((int(W * 0.78), int(H * 0.20)), "Página %s" % hoja, font=F(24), fill=NEGRO)
    y = int(H * 0.23)
    d.rectangle([int(W * 0.06), y, int(W * 0.94), y + 46], outline=NEGRO, width=2)
    for tx, fx in [("Pos.", 0.07), ("Cuenta", 0.13), ("Descripción", 0.28), ("Importe", 0.83)]:
        d.text((int(W * fx), y + 11), tx, font=F(24, True), fill=NEGRO)
    y += 46
    for i, m in enumerate(montos):
        d.rectangle([int(W * 0.06), y, int(W * 0.94), y + 46], outline=GRIS, width=1)
        d.text((int(W * 0.07), y + 11), "%03d" % (i + 1), font=F(22), fill=NEGRO)
        d.text((int(W * 0.13), y + 11), "52114110%02d" % (i + 21), font=F(22), fill=NEGRO)
        d.text((int(W * 0.28), y + 11), "MATERIALES Y SUMINISTROS DE PRUEBA", font=F(22), fill=NEGRO)
        d.text((int(W * 0.83), y + 11), m, font=F(22), fill=NEGRO)
        y += 46
    total = sum(float(m.replace(",", "")) for m in montos)
    d.text((int(W * 0.62), y + 26), "Monto Neto a Pagar", font=F(26, True), fill=NEGRO)
    d.text((int(W * 0.83), y + 26), "{:,.2f}".format(total), font=F(26, True), fill=NEGRO)
    sello(d, int(W * 0.72), int(H * 0.60), "REVISADO", AZUL, 170)
    celdas_firma(d, firmas, tapar_una)
    return escanear(im, random.uniform(-1.6, 1.6))


def pagina_soporte(tipo, n):
    im = papel(); d = ImageDraw.Draw(im)
    if tipo == "solicitud":
        d.text((int(W * 0.30), int(H * 0.09)), "SOLICITUD DE PAGO", font=F(38, True), fill=NEGRO)
        d.text((int(W * 0.06), int(H * 0.14)), "DEPENDENCIA: DEPENDENCIA DE PRUEBA", font=F(24, True), fill=NEGRO)
    else:
        d.text((int(W * 0.14), int(H * 0.09)), "LIBERACIÓN DE TRANSFERENCIAS A ENTIDADES PÚBLICAS", font=F(30, True), fill=NEGRO)
        d.text((int(W * 0.40), int(H * 0.14)), "FOLIO No. A%04d/2021" % n, font=F(24, True), fill=NEGRO)
    y = int(H * 0.22)
    for i in range(12):
        d.text((int(W * 0.08), y), "Concepto de prueba %02d ................ %s"
               % (i, "{:,.2f}".format(random.uniform(100, 9000))), font=F(23), fill=NEGRO)
        y += 46
    sello(d, int(W * 0.55), int(H * 0.72), "RECIBIDO", AZUL, 165)
    garabato(d, int(W * 0.60), int(H * 0.86), 300, 60)
    return escanear(im, random.uniform(-1.2, 1.2))


pgs = []
ordenes = [
    ("1900000001", ["12,500.00", "3,480.50"], 3, None, False, True),   # sello encima de una firma
    ("1900000002", ["45,000.00"], 2, None, True, False),               # raya de pluma sobre el número
    ("1900000003", ["1,200.00", "900.00", "7,315.20"], 1, "1 / 2", False, False),
    ("1900000003", ["2,000.00"], 0, "2 / 2", False, False),            # hoja 2: sin firmas
    ("7100000123-A", ["18,750.00"], 3, None, False, False),            # ADEFA
    ("5100000055", ["3,900.00"], 2, None, False, False),               # otra serie
]
for i, (num, montos, firmas, hoja, raya, tapar) in enumerate(ordenes):
    pgs.append(pagina_orden(num, montos, firmas, hoja, raya, tapar))
    pgs.append(pagina_soporte("solicitud", i + 1))
    pgs.append(pagina_soporte("liberacion", i + 1))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pgs[0].save("op-sintetico.pdf", save_all=True, append_images=pgs[1:], resolution=200.0)
print("listo: op-sintetico.pdf con", len(pgs), "páginas")
