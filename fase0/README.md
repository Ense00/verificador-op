# Fase 0 — medir qué se puede leer de los PDF

Antes de programar la verificación de verdad hay que saber, con un PDF real, qué
tan lejos llega el navegador. Esta carpeta trae el **medidor**: una página que
abre un PDF y reporta, página por página, qué logró leer y cuánto tardó.

## Cómo usarlo

```bash
~/Documents/Dev/verificador-op/fase0/servir.sh
```

Eso levanta un servidor local y abre el medidor. Luego: elegir el PDF, un rango
de páginas (empieza con 10–15) y presionar **Medir**.

El PDF **no sale de la computadora**: todo se procesa en el navegador. De
internet solo bajan las librerías (pdf.js, Tesseract) y el idioma del OCR, y solo
la primera vez.

## Qué mide

| Qué | Para qué sirve |
|---|---|
| Si la página ya trae texto | Si el PDF no es puro escaneo, el OCR sobra y todo es 10× más rápido |
| Tiempo de render y de OCR | Saber si 3,000 páginas se pueden verificar en el navegador o hace falta un programa instalable |
| Número de orden leído (incluido `-A`) | Es lo mínimo indispensable: sin número no hay verificación. Un número de orden es cualquier grupo de **10 dígitos**: en los documentos base reales todas lo son, y las series son varias (19, 50, 51, 71) |
| Folio | Hay órdenes que usan el folio como número de orden; se muestra y se marca si tiene forma de orden |
| Números de 8 a 12 dígitos | Delatan al OCR cuando pierde o inventa un dígito |
| Montos y fechas leídos | Para cotejar contra el documento base |
| Clase de página (orden / soporte / dudosa) | Los PDF mezclan órdenes con facturas y anexos |
| Líneas de firma y cuáles traen tinta | El conteo de firmas (3 esperadas) es la regla más delicada |
| Tinta, color e inclinación | Calidad del escaneo: sellos de color, hojas chuecas |

En "Revisar una página" se ve la página **ya enderezada**, con las líneas
detectadas en rojo y en azul la franja donde se busca la firma. Ahí se nota
rápido si la detección se equivocó.

**Exportar medición (JSON)** guarda los números para compararlos entre corridas.
Por omisión no incluye el texto leído; si se marca la casilla, el archivo queda
con datos del documento y hay que tratarlo como tal.

## Cómo está hecha la detección de firmas

1. Se pasa la página a gris y se binariza con Otsu.
2. Se estima la inclinación probando ángulos de −3° a 3°: gana el que deja más
   renglones alineados. **Sin enderezar no se detecta nada**: una raya inclinada
   1.5° no cae en una sola fila de píxeles.
3. Se buscan, en cada fila, todas las corridas oscuras largas y **sólidas**
   (una raya está llena de tinta; un renglón de texto tiene huecos entre letras).
   Tienen que ser todas las de la fila: las tres líneas de firma están a la misma
   altura.
4. Se descartan las demasiado largas (bordes de tabla) y las demasiado cortas.
5. Sobre cada línea se mide la tinta de la franja de arriba: si tiene bastante
   más que el promedio de la página, se cuenta como firmada.

Los umbrales (largo de línea, solidez, tinta de la franja) son un punto de
partida: se ajustan con el PDF real, que es justo para lo que sirve esta página.

## Probarla sin PDF real

```bash
python3 fase0/generar-pdf-de-prueba.py
```

Deja aquí un `op-sintetico.pdf` con datos inventados que imita un escaneo:
órdenes con 3, 2, 1 y 0 firmas, una orden de dos hojas, una ADEFA `-A`, un sello
encima de una firma, un folio arriba y dos páginas de soporte. El archivo está
bloqueado en `.gitignore`.

Con ese PDF el medidor acierta las 7 páginas en clase, número de orden, líneas y
firmas, y tarda ~1.2 s por página a 150 ppp (render 170 ms + OCR 900 ms). Es un
escaneo *limpio*: con papel real hay que esperar peor.
