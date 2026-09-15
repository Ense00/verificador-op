# Requisitos — Verificador de Órdenes de Pago

Documento vivo: aquí se registra lo que la herramienta debe hacer. Cada cambio de criterio se anota también en `CHANGELOG.md`.

## Problema

Se descarga una carpeta de PDFs **escaneados** con Órdenes de Pago (OP). Un PDF puede traer 1 OP en pocas páginas o cientos de OP en 500–3000+ páginas. Hay que comprobar, contra un Excel, que cada OP solicitada esté en la carpeta y sea válida.

## Flujo completo del proceso

1. **Documento base** (Excel exportado del sistema, uno por entidad y ejercicio): trae órdenes de pago, montos y muchas columnas más. Es la fuente de **todo**: del Layout y de la verificación.
2. **Layout:** a partir del documento base se genera un Excel con formato fijo que se sube a una plataforma externa.
3. **Plataforma:** con el Layout, extrae y entrega los PDFs de las órdenes solicitadas.
4. **Verificación:** se revisan esos PDFs contra el documento base (lo descrito en el resto de este documento).

### Documento base (estructura observada en un ejemplo real)

- Una hoja, encabezados en la fila 1. Columnas relevantes: `Contribución` (nombre de la entidad), `Orden de Pago` (10 dígitos, guardada como texto), `Fecha Contable` (fecha), `Importe en moneda de la entidad CP` (monto). Otras columnas (`DocReferencia`, `Período`, `Status Actual`, `Centro gestor`, etc.) no se usan para verificar.
- `DocReferencia` **no** es la orden de pago; no usarla.
- La última fila puede ser un **total con fórmula** sin orden de pago: se ignora toda fila sin orden de pago.
- Puede haber **montos negativos**.
- Una orden de pago puede repetirse en varias filas con montos distintos.
- Hay series de orden que empiezan con `19` y con `71`.

### Layout para la plataforma

Plantilla: hoja `Hoja1`, 8 columnas con estos encabezados exactos. La plataforma es imperfecta: **no** llenar según el nombre de la columna, sino así:

| Columna | Valor |
|---|---|
| `DocumentoReferencia` | Orden de pago |
| `OrdenPago` | Orden de pago |
| `FechaContable` | vacío |
| `Periodo` | Año del ejercicio |
| `CentroGestor` | vacío |
| `PeriodoPresupuesto` | Año del ejercicio |
| `Importe` | vacío |
| `PartidaGasto` | vacío |

- **Todo en formato número, sin decimales** (enteros).
- **Sin órdenes repetidas:** la plataforma marca error. Una fila por orden de pago única. (En la verificación sí se conservan las repeticiones con montos distintos.)
- Nombre de archivo: `Layout ｜ [Entidad] ｜ [Ejercicio] ｜ [Fecha] ｜ [Hora].xlsx`.

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

### Nombre de la entidad y nombres de archivo

- La configuración tiene un campo **Nombre de la entidad** (obligatorio para descargar). Se recuerda en el navegador para la siguiente vez.
- Formato: `[Tipo] ｜ [Entidad] ｜ [Ejercicio] ｜ [Fecha] ｜ [Hora]`
  - **Separador:** ` ｜ ` (espacio, barra de ancho completo U+FF5C, espacio). El usuario pidió `|`, pero Windows no lo permite en nombres de archivo; U+FF5C se ve igual y sí está permitido. Contras aceptados: no se puede teclear para buscar y algún programa viejo podría mostrarlo raro.
  - **Tipo:** `Tabla` para el Excel de resultados; *vacío* para la carpeta o comprimido (el nombre empieza directo con la entidad, sin separador inicial); `Layout` para un archivo que el usuario explicará más adelante.
  - **Ejercicio:** el del Excel de entrada; si trae varios, rango `2021-2022`.
  - **Fecha y hora:** momento en que se crea el archivo. Formato `DD-MM-AAAA` y `HH-MM` (24 h). Día primero para que el año de la fecha no se confunda con el ejercicio que va justo antes; la hora con guion porque Windows no permite `:` en nombres. *Confirmado.*
  - Se quitan de la entidad los caracteres que Windows no permite: `\ / : * ? " < > |`, y también `｜` para no confundir el separador.
- Ejemplos: `Tabla ｜ Entidad de Ejemplo ｜ 2021 ｜ 14-09-2026 ｜ 16-05.xlsx` y `Entidad de Ejemplo ｜ 2021 ｜ 14-09-2026 ｜ 16-05.zip`.

### Excel de resultados

- **Con diseño**, misma identidad que la página: título en banda azul tinta, fila con entidad/ejercicio/fecha de generación/conteos, encabezados con color (validaciones en otro tono), filas alternadas, bordes finos, Estado y validaciones con color por estado, montos con formato `$#,##0.00`, filtros, encabezado y primera columna fijos, sin cuadrícula y color de pestaña por hoja. (La librería gratuita SheetJS no escribe estilos; se usa ExcelJS.)

- **Verificación:** columnas de lo marcado en "Qué revisar" + Estado + Motivo + Archivo (nombre nuevo) + Página.
- **No encontradas.**
- **Duplicados omitidos:** archivo omitido y de cuál es copia.
- **Renombres** *(opcional, casilla)*: nombre original → nombre nuevo.

### Carpeta de archivos

PDFs sin duplicados y ya renombrados, más la subcarpeta de revisión manual. Formato elegible, **ZIP por defecto**; otras opciones de formatos universales (por definir tras medir). RAR descartado: formato propietario que no se puede generar libremente.

## Recomendaciones para la versión real

Acordadas durante el diseño del boceto. No son opcionales: son parte de lo que la herramienta debe cumplir.

### Volumen

- Debe soportar corridas especiales de hasta **3,000 órdenes** (estimado: 6,000–15,000 páginas únicas) y archivos individuales de 3,000+ páginas.

### Tabla

- **Tabla virtualizada:** solo se dibujan las filas visibles (~40) y se reemplazan al desplazarse. Filtrar, buscar, cambiar casillas y navegar con ↑ ↓ debe sentirse instantáneo con 3,000 filas o más.
- La vista previa y la navegación con teclado funcionan igual sin importar la cantidad de filas.

### Velocidad del análisis

- **Duplicados primero:** descartar archivos idénticos por huella antes de leer cualquier página.
- **Leer solo zonas de interés** (número, año, tabla de montos) en lugar de la página completa; firmas y sellos se revisan por análisis de imagen, sin OCR.
- **Procesamiento en paralelo:** usar varios núcleos del procesador a la vez (Web Workers).
- **Medir antes de prometer:** el tiempo por página se mide con escaneos reales en la computadora del trabajo. Estimación inicial muy gruesa para 10,000 páginas: 20 min a 1 h.

### Corridas largas sin fragilidad

- **Progreso guardado en el navegador:** si se cierra la pestaña, se reinicia la computadora o se va la luz, el análisis se reanuda donde se quedó.
- **Avance con tiempo estimado:** p. ej. "Página 4,210 de 11,380 · faltan ~18 min".
- **Evitar que la computadora se suspenda** mientras analiza (Wake Lock).
- **Memoria bajo control:** no guardar imágenes de páginas; la vista previa vuelve a dibujar la página desde el PDF al seleccionarla.

### Uso

- La configuración se oculta sola al terminar la verificación y deja una línea con lo elegido.
- "Marcar revisado": corregir a mano el resultado de una orden después de revisarla; queda anotado en el Excel.
- Página instalable (app web) para que funcione sin internet incluso al abrirla.

## Pendiente

- Layout: de dónde sale el ejercicio, montos negativos, límite de filas de la plataforma, autollenar entidad desde `Contribución`.

- PDF de ejemplo (con una OP válida, una con solo 2 de 3 firmas, una con varios montos y una con sello sobre firma) para la fase 0: medir lectura, enderezado, detección de firmas/sellos y velocidad en navegador.
