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
- Puede haber **montos negativos**: se verifican y se marcan como *Revisar* ("Monto negativo en el documento base").
- Una orden de pago puede repetirse en varias filas con montos distintos.
- Hay series de orden que empiezan con `19` y con `71`.
- Pueden aparecer órdenes **con y sin** sufijo `-A` (ADEFA).
- **Ejercicio = año de la `Fecha Contable`** de cada fila.
- **Las columnas pueden cambiar de posición, pero no de nombre:** se localizan por el nombre del encabezado (sin distinguir mayúsculas, acentos ni espacios extra).
- El nombre de la entidad se escribe **a mano** en la página (la columna `Contribución` no siempre trae el nombre completo).

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

- **Todo en formato número, sin decimales** (enteros). **Excepción:** las órdenes ADEFA (`-A`) van tal cual como texto, con formato **General**.
- **Sin órdenes repetidas:** la plataforma marca error. Una fila por orden de pago única (la original y su `-A` cuentan como órdenes distintas; ambas van). (En la verificación sí se conservan las repeticiones con montos distintos.)
- Nombre de archivo: `Layout ｜ [Entidad] ｜ [Ejercicio] ｜ [Fecha] ｜ [Hora].xlsx`.
- La plataforma no tiene límite práctico de filas.
- **Partir Layout** (opcional): N partes iguales (difieren en máximo 1 orden), sin órdenes repetidas, en el orden en que aparecen en el documento base. Cada archivo termina en ` ｜ Parte K` y se pueden descargar juntas en un ZIP o una por una. Mismo documento + mismo N = mismas partes.
- En la verificación se puede elegir **qué parte se está verificando**, para que las órdenes de otras partes no salgan como "No encontradas" (idea propuesta en v0.5.0, aprobada por el usuario el 2026-09-16):
  - "Layout partido en N partes" es **el mismo número** que "Partir Layout" en la etapa 1: cambiarlo en una etapa lo cambia en la otra. 1 = sin partir.
  - "Parte a verificar": Todas las órdenes, o Parte K de N (la lista sale de N, no es fija).
  - Las órdenes de cada parte se calculan con el **mismo reparto** que "Partir Layout" sobre el documento base, así que coinciden con el Layout que se subió a la plataforma. Si el documento base está cargado, se muestra cuántas órdenes se esperan y de cuál a cuál.
  - Requisito: usar el mismo documento base con el que se generó el Layout; con otro documento las partes no coinciden.
  - Las partes se reparten por **órdenes únicas** (cada orden en la parte de su primera aparición). Al verificar una parte se toman esas órdenes **con todas sus filas** del documento base (todos sus montos), aunque las filas repetidas estén lejos en el Excel. Ejemplo: 10 órdenes con repeticiones partidas en 10 → cada parte es 1 orden con todas sus filas.

### PDFs: órdenes de pago mezcladas con documentos de soporte

- Los PDFs **no traen solo órdenes de pago**: cada orden va acompañada de su documentación de soporte (transferencias bancarias, detalles, etc.), todo en el mismo archivo.
- La herramienta debe **distinguir qué páginas son orden de pago** y cuáles son soporte, y validar solo las de orden de pago.
- Riesgo a cuidar: el soporte puede mencionar el número de orden (p. ej. la referencia de una transferencia). El número, el ejercicio, los montos, las firmas y los sellos se leen **solo de la página de la orden**, nunca del soporte.
- Ventaja: identificar las páginas de soporte antes de leerlas permite **saltarse su OCR** y acelerar el análisis.
- **El orden de las páginas varía:** el soporte puede ir antes, después o entre páginas de la orden. No se puede asumir "orden → soporte".
- **Una orden puede ocupar varias hojas:** listas de montos largas que continúan en otras páginas y firmas en una página aparte. La orden se arma como un solo documento (primera hoja + continuaciones + hoja de firmas); montos se buscan en todas sus hojas y firmas en la hoja de firmas.
- **Orden partida y desordenada** (sus hojas regadas entre la documentación, sin orden): poco común. No se intenta rearmar: **Incorrecto** con motivo "Orden partida y desordenada en el PDF: revisar manualmente".
- **Ubicación del número:** no siempre está en la esquina superior. Puede haber un **número de folio** arriba (que no es la orden) y el número de orden debajo o cerca del centro. Se busca en toda la página y solo cuenta un número que corresponda a una orden del documento base; el folio se ignora y no genera "número distinto".
- **Órdenes ADEFA** (Adeudos de Ejercicios Fiscales Anteriores), con sufijo `-A` (p. ej. `1900000000-A`): continuación de una orden original cuyo monto no se pagó completo; se siguen pagando en ejercicios posteriores. Solo existe el sufijo `-A` (no `-B`, `-C`).
  - Son **órdenes distintas** de su original: montos propios y pueden tener firmas diferentes.
  - En los PDFs suelen venir junto a la original sin sufijo.
  - **Verificación exacta:** si se pide `…-A` se busca la `-A`; si se pide la original, la original. Nunca se cruzan.
  - La original y su `-A` **no** son duplicados (son números distintos): no van a Revisión manual por eso.
  - Que una página de `-A` muestre también el número original **no** es "número distinto".
  - Riesgo de lectura: si no se puede confirmar si el sufijo `-A` está o no, el resultado es *Ilegible*, nunca se asume.
- **Soporte:** no se valida (solo en casos extraordinarios de datos incorrectos, que se revisan a mano).
- **Orden sin soporte** o **soporte sin orden:** **Revisar**.

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
| Firmas | Deben ser **3 firmas en total**, a mano, en la parte inferior. Los cargos de quienes firman varían, así que no se valida quién firma, solo que sean 3. Una orden puede traer **0, 1, 2 o 3 firmas**: se reporta el conteo ("Sin firmas (0 de 3)", "Solo 1 de 3 firmas", "Solo 2 de 3 firmas"). Frecuencia real: lo común es que **falte 1 firma**; **sin firmas** es raro y suele estar justificado, pero se marca como **Incorrecto** con su motivo (el usuario lo corrige con "Corregir estado" si está justificado); **1 de 3** prácticamente no ocurre. Solo se detecta presencia, no autenticidad |
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

Se **descarta la plantilla fija** (una orden bien escaneada como referencia de posiciones): las órdenes no respetan un solo acomodo (hojas de continuación, firmas en hoja aparte, folio arriba o no, número en distintas posiciones). Nada depende de coordenadas fijas.

Por página: enderezar → limpiar → clasificar → leer → validar.

1. **Enderezar sin plantilla:** rotación 90°/180° y corrección de inclinación a partir de las líneas de texto y los bordes de tablas de la propia página.
2. **Limpiar:** binarización adaptativa, contraste.
3. **Clasificar la página por su contenido**, no por posición: orden de pago (primera hoja), continuación de lista de montos, hoja de firmas o soporte. Señales: textos que siempre aparecen (título, etiquetas de campos, "TOTAL"), estructura de tabla, líneas de firma con nombre y cargo debajo.
4. **Leer buscando, no en zonas fijas:** número de orden = cualquier número de la página que coincida con una orden del documento base (incluido `-A`); montos = importes en la tabla/lista; firmas = trazos sobre las líneas de firma que se detecten, estén donde estén; sellos = manchas circulares/rectangulares de tinta azul o negra.
5. **OCR completo de la página** cuando haga falta (las zonas ya no son fijas); para compensar velocidad, primero una clasificación barata para saltarse el soporte.

*A validar en la fase 0 con PDFs reales:* qué elementos aparecen siempre en todas las variantes (para clasificar) y si alguna variante sí conviene tratarla con plantilla.

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
- **Parte:** si se verifica una parte de un Layout partido, el Excel y la carpeta terminan en ` ｜ Parte K`, igual que el Layout de esa parte (pedido del usuario, 2026-09-16: si no, no se distingue de una verificación completa). La fila de datos del Excel también dice `Parte K de N`. Ejemplo: `Tabla ｜ BOMBEROS ｜ 2021 ｜ 16-09-2026 ｜ 17-54 ｜ Parte 10.xlsx`.

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
- **Clasificar primero** con un análisis barato para no leer a detalle las páginas de soporte; firmas y sellos se revisan por análisis de imagen, sin OCR.
- **Procesamiento en paralelo:** usar varios núcleos del procesador a la vez (Web Workers).
- **Medir antes de prometer:** el tiempo por página se mide con escaneos reales en la computadora del trabajo. Estimación inicial muy gruesa para 10,000 páginas: 20 min a 1 h.

### Corridas largas sin fragilidad

- **Progreso guardado en el navegador:** si se cierra la pestaña, se reinicia la computadora o se va la luz, el análisis se reanuda donde se quedó.
- **Avance con tiempo estimado:** p. ej. "Página 4,210 de 11,380 · faltan ~18 min".
- **Evitar que la computadora se suspenda** mientras analiza (Wake Lock).
- **Memoria bajo control:** no guardar imágenes de páginas; la vista previa vuelve a dibujar la página desde el PDF al seleccionarla.

### Uso

- La configuración se oculta sola al terminar la verificación y deja una línea con lo elegido.
- **Corrección manual de estado** (desde la vista previa, "Corregir estado"):
  - Se elige el nuevo estado y se escribe una **nota obligatoria** (p. ej. "Sin firmas, justificado por oficio 123/2021").
  - Si la orden tiene varias filas, se puede aplicar a todas.
  - En la tabla: estado nuevo + marca ✎; filtro "Corregidas a mano"; los conteos del resumen se actualizan.
  - Se puede editar o deshacer (vuelve el estado detectado).
  - En el Excel, hoja Verificación: **Estado final**, **Estado detectado** y **Nota de corrección**; el título incluye cuántas se corrigieron.
  - Las correcciones forman parte del progreso guardado.
- Página instalable (app web) para que funcione sin internet incluso al abrirla.
- Selector de tema **Claro / Oscuro / Automático** en el encabezado; se recuerda en el navegador. Automático sigue el tema del sistema (o del visor de Claude).

## Guía de uso

- Botón **Guía** en el encabezado (junto al tema): abre una vista con índice lateral y 10 secciones para compañeros que nunca han usado la herramienta: qué es, antes de empezar, Preparar Layout, subir a la plataforma, Verificar órdenes, leer resultados, corregir estado, descargas, reglas y preguntas frecuentes. Botones para ir directo a cada etapa y "Volver a la herramienta".
- Lo que depende de la fase 0 (elegir PDFs y documento base en la etapa 2, Verificar, carpeta de archivos) va marcado **Próximamente**; la guía remite a "Ver demostración".
- **Mantenerla al día:** todo cambio de interfaz o de reglas se refleja también en la guía.
- Aprobada por el usuario tal cual (2026-09-16): "Está muy bien, déjalo así". No hace falta el Word descargable.

## Pendiente

Estado al 2026-09-16 (v0.8.0), en pausa hasta tener un PDF de órdenes:

- **Etapa 1, Preparar Layout: funcional** y probada por el usuario con un documento base real.
- **Etapa 2, Verificar órdenes:** interfaz lista; arranca vacía y ofrece "Ver demostración" con 3,000 órdenes de muestra (filtros, vista previa, corrección manual, Excel con diseño). No procesa PDFs todavía.
- La página ya no muestra avisos de boceto: el usuario pidió que se parezca lo más posible a la versión final.

Siguiente paso:

1. **Conseguir un PDF de ejemplo tal cual sale de la plataforma**, con datos sensibles tapados pero zonas de firmas y sellos visibles. Idealmente: varias órdenes en un archivo, páginas de soporte, una orden de 3 firmas, una de 2, una sin firmas si hay, una con varios montos, una de varias hojas, una con sello sobre firma, una con folio arriba y una ADEFA (`-A`).
2. **Fase 0 (medición):** con ese PDF medir en el navegador: separación orden/soporte, lectura del número (incluido `-A`), ejercicio y montos, conteo de firmas, detección de sellos, enderezado y tiempo por página.
3. Con los números de la fase 0, decidir cómo construir la verificación real (página web vs. programa instalable si el navegador se queda corto).
