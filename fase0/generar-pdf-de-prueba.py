#!/usr/bin/env python3
"""Genera un PDF de prueba que imita un escaneo de Órdenes de Pago.

Todo es ficticio (institución inventada, órdenes 1900000001…, montos al azar) y
el PDF que produce está bloqueado en .gitignore. Sirve para probar el medidor
sin usar documentos reales:

    python3 fase0/generar-pdf-de-prueba.py   # deja op-sintetico.pdf aquí

Trae: órdenes con 3, 2, 1 y 0 firmas, una orden de dos hojas, una ADEFA (-A),
un sello encima de una firma, un folio arriba y dos páginas de soporte.
Requiere Pillow.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
random.seed(7)
W,H=1700,2200  # ~200ppp carta
F=lambda s,b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"%("-Bold" if b else ""),s)

def papel():
    im=Image.new("RGB",(W,H),(252,251,248)); return im

def escanear(im,ang):
    im=im.rotate(ang,expand=False,fillcolor=(250,249,246),resample=Image.BICUBIC)
    im=im.filter(ImageFilter.GaussianBlur(0.6))
    px=im.load()
    for _ in range(90000):
        x=random.randrange(W); y=random.randrange(H); v=random.randint(-28,10)
        r,g,b=px[x,y]; px[x,y]=(max(0,min(255,r+v)),max(0,min(255,g+v)),max(0,min(255,b+v)))
    return im

def firma(d,x,y,w,color=(25,32,80)):
    px,py=x,y
    for i in range(70):
        nx=x+w*i/70+random.randint(-6,6); ny=y-random.randint(0,34)-12
        d.line([(px,py),(nx,ny)],fill=color,width=4); px,py=nx,ny

def lineas_firma(d,y,firmas):
    anchos=[(150,570),(640,1060),(1130,1550)]
    etq=["ELABORÓ","REVISÓ","AUTORIZÓ"]
    for i,(x0,x1) in enumerate(anchos):
        d.line([(x0,y),(x1,y)],fill=(40,45,60),width=3)
        d.text((x0+40,y+14),etq[i],font=F(22),fill=(60,65,80))
        d.text((x0+40,y+46),"Nombre y firma",font=F(20),fill=(90,95,110))
        if i<firmas: firma(d,x0+60,y-8,x1-x0-140)

def pagina_op(num,montos,firmas,hoja=None,sello=False,folio=False):
    im=papel(); d=ImageDraw.Draw(im)
    if folio: d.text((1380,60),"FOLIO 0%03d"%random.randint(1,999),font=F(26),fill=(120,30,30))
    d.text((150,150),"INSTITUTO DEMOSTRATIVO DE PRUEBA",font=F(34,True),fill=(20,28,56))
    d.text((150,200),"ORDEN DE PAGO",font=F(44,True),fill=(20,28,56))
    d.text((1150,205),"No. %s"%num,font=F(32,True),fill=(20,28,56))
    d.text((150,270),"Fecha contable:  15/07/2021",font=F(26),fill=(40,45,60))
    d.text((700,270),"Ejercicio:  2021",font=F(26),fill=(40,45,60))
    if hoja: d.text((1150,270),"Hoja %s"%hoja,font=F(26),fill=(40,45,60))
    y=360
    d.rectangle([150,y,1550,y+50],outline=(40,45,60),width=2)
    for tx,xx in [("PARTIDA",170),("CONCEPTO",420),("IMPORTE",1330)]:
        d.text((xx,y+13),tx,font=F(24,True),fill=(20,28,56))
    y+=50
    for i,m in enumerate(montos):
        d.rectangle([150,y,1550,y+52],outline=(120,125,140),width=1)
        d.text((170,y+14),"3%02d1"%(i+3),font=F(24),fill=(40,45,60))
        d.text((420,y+14),"Servicio de prueba numero %d"%(i+1),font=F(24),fill=(40,45,60))
        d.text((1330,y+14),m,font=F(24),fill=(40,45,60))
        y+=52
    d.text((1100,y+30),"TOTAL",font=F(28,True),fill=(20,28,56))
    tot=sum(float(m.replace(",","")) for m in montos)
    d.text((1300,y+30),"{:,.2f}".format(tot),font=F(28,True),fill=(20,28,56))
    lineas_firma(d,1780,firmas)
    if sello:
        d.ellipse([560,1660,900,1860],outline=(40,60,160),width=6)
        d.text((620,1740),"PAGADO",font=F(40,True),fill=(40,60,160))
    return escanear(im,random.uniform(-1.6,1.6))

def pagina_soporte(n):
    im=papel(); d=ImageDraw.Draw(im)
    d.text((150,160),"FACTURA A-%d"%n,font=F(38,True),fill=(30,35,50))
    d.text((150,230),"Proveedor Demostrativo S.A. de C.V.",font=F(26),fill=(40,45,60))
    d.text((150,275),"RFC: XAXX010101000",font=F(24),fill=(40,45,60))
    y=380
    for i in range(14):
        d.text((150,y),"Concepto de prueba %02d ................. %s"%(i,"{:,.2f}".format(random.uniform(100,9000))),font=F(23),fill=(45,50,65))
        y+=46
    d.text((150,1200),"Este documento es soporte y no se verifica.",font=F(24),fill=(80,85,100))
    return escanear(im,random.uniform(-1.2,1.2))

pgs=[
 pagina_op("1900000001",["12,500.00","3,480.50"],3,sello=True),
 pagina_soporte(1),
 pagina_op("1900000002",["45,000.00"],2,folio=True),
 pagina_op("1900000003",["1,200.00","900.00","7,315.20"],1,hoja="1 de 2"),
 pagina_op("1900000003",["2,000.00"],0,hoja="2 de 2"),
 pagina_soporte(2),
 pagina_op("7100000123-A",["18,750.00"],3),
]
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pgs[0].save("op-sintetico.pdf",save_all=True,append_images=pgs[1:],resolution=200.0)
print("listo: op-sintetico.pdf con", len(pgs), "páginas")
