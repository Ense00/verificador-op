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
| Qué documento es cada página | Los PDF traen órdenes mezcladas con solicitudes, liberaciones y comprobantes del banco. Se decide por el encabezado |
| Número de orden (incluido `-A`) | Se lee solo en las páginas de orden, de la caja de arriba a la derecha |
| Confirmación contra el documento base | Pegando ahí la lista de órdenes solicitadas, el medidor **confirma** el número en vez de solo reportarlo |
| Tinta de color en las tres celdas del pie | Es el conteo de firmas: la firma es de pluma, el nombre impreso es negro |
| Tiempos de render, encabezado y número | Para saber si 3,000 páginas se pueden verificar en el navegador |
| Si la página ya trae texto | Si el PDF no es puro escaneo, el OCR sobra |
| Inclinación y color de la página | Calidad del escaneo |

En "Revisar una página" se ve la página con las zonas marcadas: en rojo donde se
busca el número, en azul las tres celdas de firma (llenas si tienen tinta).

**Exportar medición (JSON)** guarda los números para comparar corridas. Por
omisión no incluye el texto leído ni los números de orden; si se marca la
casilla, el archivo queda con datos del documento y hay que tratarlo como tal.

## Lo que se aprendió midiendo un PDF real

1. **300 ppp de render.** El escaneo viene a 200 ppp; a menos de 300 el número no se lee.
2. **Borrar la tinta de color antes de leer.** La impresión es negra; pluma y sellos traen color. Una raya de pluma encima de los dígitos arruina el OCR, y blanquear el color lo resuelve.
3. **Leer zonas, no páginas.** El OCR de la página completa tarda 2.9 s y ni así lee el número chico. Dos recortes (encabezado y caja del número) bajan a 0.55 s por página y aciertan.
4. **`PSM 4`, nunca `PSM 6`.** Con `PSM 6` no se leyó ni una sola orden; con `PSM 4` salieron todas.
5. **Varios intentos.** La caja se mueve con el escaneo: se prueban cinco recortes y escalas hasta que uno coincide con el documento base.
6. **La `A` de ADEFA va en la lista de caracteres** y pegada al número; si no, una `-A` se confunde con su original.
7. **El documento base es el árbitro.** Los PDF están llenos de números de 10 dígitos que no son órdenes.

## Probarla sin PDF real

```bash
python3 fase0/generar-pdf-de-prueba.py
```

Deja aquí un `op-sintetico.pdf` con datos inventados que imita un escaneo:
órdenes con 3, 2, 1 y 0 firmas, una orden de dos hojas, una ADEFA `-A`, un sello
encima de una firma, un folio arriba y dos páginas de soporte. El archivo está
bloqueado en `.gitignore`.

Imita el formato real: seis órdenes, cada una seguida de su solicitud y su
liberación, con los casos difíciles (raya de pluma sobre el número, sello encima
de una firma, ADEFA `-A`, orden de dos hojas, otra serie). El medidor acierta las
seis en clasificación y en conteo de firmas (3, 2, 1, 0, 3 y 2), y lee el número
en cinco de seis: falla justo la que lleva la raya gruesa encima de los dígitos,
que queda como "no se leyó" en vez de adivinada.
