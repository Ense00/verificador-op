# Requisitos — Verificador de Órdenes de Pago

Documento vivo: aquí se registra lo que la herramienta debe hacer. Cada cambio de criterio se anota también en `CHANGELOG.md`.

## Problema

Se descarga una carpeta de PDFs **escaneados** con Órdenes de Pago (OP). Un PDF puede traer 1 OP en pocas páginas o cientos de OP en 500–3000+ páginas. Hay que comprobar, contra un Excel, que cada OP solicitada esté en la carpeta y sea válida.

## Principios

- **Privacidad:** los PDFs y el Excel se procesan en la computadora del usuario (en el navegador). Nada se sube a servidores ni a servicios de IA.
- **Nunca adivinar:** si no hay certeza, el resultado es *Revisar* o *Ilegible*, nunca *Correcto*.
- **Los archivos originales no se modifican.** Todo cambio (renombres, carpetas) se aplica en la salida.

## Entrada

- Carpeta con PDFs escaneados (mismo formato de OP en todos).
- Excel con las OP solicitadas. Columnas habituales: `Op`, `Ejercicio`, `Monto` (opcional), `Notas` (texto libre del usuario, no estructurado).
  - Una misma OP puede aparecer en varias filas con montos distintos.
  - La celda de monto puede venir vacía → ese renglón no se valida por monto.

## Qué revisar (casillas elegibles por corrida)

| Casilla | Regla |
|---|---|
| Orden de pago | El número mencionado y el mostrado en el documento coinciden, y corresponden al Excel |
| Ejercicio | Solo importa el **año**; debe ser el del Excel |
| Monto | El monto solicitado debe aparecer **en algún lugar de la lista** de montos de la OP (una línea o el total), al centavo. Si hay uno casi igual, se menciona (p. ej. "difiere por $0.01") |
| Firmas | Deben ser **3 firmas en total**, a mano, en la parte inferior. Los cargos de quienes firman varían, así que no se valida quién firma, solo que sean 3 (p. ej. "Solo 2 de 3 firmas"). Solo se detecta presencia, no autenticidad |
| Sellos | Azules o negros, en cualquier posición, a veces encima de firmas. Sello encima de firma = *Revisar* |

Localizar la OP en los PDFs se hace siempre (es la base de todo). Lo no marcado sale como "No revisado".

## Estados

| Estado | Significado |
|---|---|
| **Correcto** | Se leyó con certeza y cumple |
| **Incorrecto** | Se leyó con certeza y no cumple (con motivo) |
| **Revisar** | Se leyó pero hay ambigüedad, o hay copias de la OP en conflicto |
| **Ilegible** | Mala calidad: no se puede leer con certeza. Se reporta por dato, no por orden completa |

Señales de ilegibilidad: confianza del OCR, que la lista de montos no sume el total, calidad de imagen (borrosa, clara, chueca).

## Procesamiento de imagen

Por página: enderezar → alinear contra plantilla → limpiar → leer → validar.

1. Detección de rotación 90°/180°.
2. Alineación contra plantilla (mismo formato): corrige inclinación, desplazamiento, escala y perspectiva; fija las zonas de firmas.
3. Respaldo: enderezado (deskew) por perfil de proyección.
4. Binarización adaptativa y limpieza.
5. OCR solo de las zonas de interés (número, año, montos) para acelerar.

## Duplicados

1. **Archivo idéntico** (misma huella de bytes): se omite sin leerlo.
2. **Página idéntica** (misma huella visual): no se vuelve a leer.
3. **OP ya verificada como Correcta** en otro archivo: no se revisa de nuevo.
4. **Dos o más archivos distintos con la misma OP y el mismo ejercicio:** los archivos van a una carpeta aparte para revisión manual, y el Excel lleva una nota explicando la situación.

## Renombres

Si un archivo trae más de una OP, se renombra con todas sus OP en orden de aparición, separadas por `_`:

- `1900000001_1900000002_1900000003.pdf`
- Si son más de 20 OP o el nombre no cabe (límite de Windows ~255 caracteres): `PrimeraOP_al_UltimaOP_(N OPs).pdf`, p. ej. `1900000001_al_1900000087_(87 OPs).pdf`

## Salida

### Excel de resultados

- **Verificación:** columnas de lo marcado en "Qué revisar" + Estado + Motivo + Archivo (nombre nuevo) + Página.
- **No encontradas.**
- **Duplicados omitidos:** archivo omitido y de cuál es copia.
- **Renombres** *(opcional, casilla)*: nombre original → nombre nuevo.

### Carpeta de archivos

PDFs sin duplicados y ya renombrados, más la subcarpeta de revisión manual. Formato elegible, **ZIP por defecto**; otras opciones de formatos universales (por definir tras medir). RAR descartado: formato propietario que no se puede generar libremente.

## Pendiente

- PDF de ejemplo (con una OP válida, una sin firma de Tesorero, una con varios montos y una con sello sobre firma) para la fase 0: medir lectura, enderezado, detección de firmas/sellos y velocidad en navegador.
